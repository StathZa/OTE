#################################### Mail protocol transfer ################################################
from utils.dependencies import smtplib, MIMEText, MIMEMultipart, MIMEApplication, os, logging, glob, Path, datetime


# ---------------------------- Helper Functions ---------------------------------------
def get_log_report(pattern: str = "energy_bills",
                   use_logs: bool = False,
                   logger: logging.Logger = None,
                   root: str = "/tmp" if os.getenv("RSTUDIO_PRODUCT") == "CONNECT" else f"{os.getcwd()}"
                  ) -> tuple:
    """Extract the contents of log report"""
    
    matches = glob(f"{root}/logs/{pattern}*.log",  recursive=True)
    
    if not matches:
        logger.warning(f"No log file matching '*{pattern}*.log' found")
        raise FileNotFoundError(f"No log file matching '*{pattern}*.log' found")
    
    log_filepath = Path(matches[0])
    logger.info(f"Log file found at {log_filepath.parent}")
    
    if use_logs:
        lines = [line for line in open(log_filepath, 'r').readlines()]    
        info = [l for l in lines if "INFO" in l]
        warnings = [l for l in lines if "WARNING" in l]
        err = [l for l in lines if "ERROR" in l]
        misc = [l for l in lines if l not in info+warnings+err]
        return (log_filepath, info, warnings, err, misc)
    else:
        lines = [line for line in open(log_filepath, 'r').read().split("\n") if line.strip()]
    
    report_text = "\n".join(lines)
    
    return (log_filepath, report_text)



def build_report_text(
    title: str = "Energy Bills Automation",
    run_by: str = "energy_user",
    env: str = "Posit Connect" if os.getenv("RSTUDIO_PRODUCT") == "CONNECT" else "Workbench",
    use_logs: bool = True,
    logger: logging.Logger = None
) -> str:
    
    # get user
    try:
        import getpass
        usr = getpass.getuser()
    except:
        usr = None
    
    info = warnings = errors = other = None
    if use_logs:
        _, info, warnings, errors, other = get_log_report(use_logs=True, logger=logger)
        
        
    sep    = "═" * 20
    thin   = "─" * 20
#     status = "FAILED" if errors is not None else "COMPLETED WITH WARNINGS" if warnings is not None else "COMPLETED SUCCESSFULLY"
    status = "FAILED" if errors else "COMPLETED WITH WARNINGS" if warnings else "COMPLETED SUCCESSFULLY"
    now    = datetime.now()

    # General Section
    lines = [
        sep,
        f"  AUTOMATED RUN REPORT",
        f"  {title}",
        sep,
        f"  Date        : {now:%d-%m-%Y}",
        f"  Time        : {now:%H:%M:%S}",
        f"  Environment : {env}",
        f"  Executed by : {run_by if not usr else usr}",
        f"  Status      : {status}",
        sep,
    ]
    
    # Relevant information according to file handler
    if info:
        lines += ["", "  SUMMARY", thin]
        lines += [f"  {l}" for l in info]

    if warnings:
        lines += ["", "  WARNINGS", thin]
        lines += [f"     {w}" for w in warnings]

    if errors:
        lines += ["", "  ERRORS", thin]
        lines += [f"     {e}" for e in errors]
        
    if other:
        lines += ["", "  OTHER INFORMATION", thin]
        lines += [f"     {misc}" for misc in other]

    # Closing Section
    lines += [
        "",
        thin,
        "  This is an automated message. Please do not reply.",
        "  For support contact: eyzacharis@groupnet.gr",
        sep,
    ]

    return "\n".join(lines)


def send_report_text(report_text: str,
                     subject: str,
                     recipients: list,
                     attachment_paths: list = None, 
                     SMTP_SERVER: str = "relay.ote.gr",
                     SMTP_PORT: int = 25,
                     SENDER: str = "EnergyServer@cosmote.gr", 
                     logger: logging.Logger = None) -> bool:
    """Establish a STMP connection to send automated responses"""
    
    msg = MIMEMultipart()
    msg["From"] = SENDER
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    msg.attach(MIMEText(report_text, "plain", _charset="utf-8"))

    for path in (attachment_paths or []):
        try:
            with open(path, "rb") as f:
                part = MIMEApplication(f.read(), _subtype="txt")
            part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(path)}"')
            msg.attach(part)
        except Exception as e:
            logger.exception(f"WARNING: could not attach {path}: {e}")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as s:
            logger.info(f"Sending email to {', '.join(recipients)}")
            s.sendmail(SENDER, recipients, msg.as_string())
            return True
    except Exception:
        logger.exception(f"Failed to send email to {', '.join(recipients)}")
        return False