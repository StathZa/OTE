# -------------------------- Lightweight pipeline profiler of script performance ----------------------------------
from utils.dependencies import pd, time, tracemalloc, logging, contextmanager, dataclass, Optional

@dataclass
class StageResult:
    name:     str
    wall_ms:  float        = 0.0
    cpu_ms:   float        = 0.0
    peak_mb:  float        = 0.0
    rows_in:  Optional[int] = None
    rows_out: Optional[int] = None
    error:    Optional[str] = None


class PipelineProfiler:

    def __init__(self, logger: logging.Logger):
        self.logger  = logger
        self.results: list[StageResult] = []
        self._t0     = time.perf_counter()

    @contextmanager
    def stage(self, name: str, df: pd.DataFrame = None):
        rows_in  = len(df) if df is not None else None
        t0_wall  = time.perf_counter()
        t0_cpu   = time.process_time()
        tracemalloc.start()
        result   = StageResult(name=name, rows_in=rows_in)
        try:
            yield result
        except Exception as exc:
            result.error = str(exc)
            self.logger.error(f"[profiler] {name}: {exc}")
            raise
        finally:
            result.wall_ms  = (time.perf_counter() - t0_wall) * 1000
            result.cpu_ms   = (time.process_time()  - t0_cpu)  * 1000
            result.peak_mb  = tracemalloc.get_traced_memory()[1] / 1024 ** 2
            result.rows_out = len(df) if df is not None else None
            tracemalloc.stop()
            self.results.append(result)
            self._log(result)

    def _log(self, r: StageResult):
        row_info = ""
        if r.rows_in is not None and r.rows_out is not None:
            d = r.rows_out - r.rows_in
            row_info = f"  rows {r.rows_in:,}→{r.rows_out:,} ({'+' if d>=0 else ''}{d:,})"
        self.logger.info(
            f"[profiler] {'Not OK' if r.error else 'OK'} {r.name:<20} "
            f"wall={r.wall_ms:>8.1f}ms  cpu={r.cpu_ms:>8.1f}ms  "
            f"peak={r.peak_mb:>6.1f}MB" + row_info
        )

    def report(self):
        sep   = "─" * 80
        total = time.perf_counter() - self._t0
        self.logger.info(sep)
        self.logger.info(f"{'Stage':<20} {'Status':<6} {'Wall(ms)':>10} {'CPU(ms)':>10} {'Peak(MB)':>10} {'Rows in':>10} {'Rows out':>10}")
        self.logger.info(sep)
        for r in self.results:
            self.logger.info(
                f"{r.name:<20} {'ERR' if r.error else 'OK':<6} "
                f"{r.wall_ms:>10.1f} {r.cpu_ms:>10.1f} {r.peak_mb:>10.1f} "
                f"{str(r.rows_in  or ''):>10} {str(r.rows_out or ''):>10}"
            )
        self.logger.info(sep)
        self.logger.info(f"Total: {total:.2f}s  |  "
                         f"Stages: {sum(1 for r in self.results if not r.error)}/{len(self.results)}")
        self.logger.info(sep)

    def summary_df(self) -> pd.DataFrame:
        return pd.DataFrame([{
            "stage":   r.name,
            "wall_ms": round(r.wall_ms, 1),
            "cpu_ms":  round(r.cpu_ms,  1),
            "peak_mb": round(r.peak_mb, 1),
            "rows_in": r.rows_in,
            "rows_out":r.rows_out,
            "delta":   (r.rows_out - r.rows_in)
                       if r.rows_in is not None and r.rows_out is not None else None,
            "error":   r.error,
        } for r in self.results])