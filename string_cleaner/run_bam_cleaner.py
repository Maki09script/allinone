import cleaner
try:
    cleaner.clean_bam_state()
except Exception as e:
    with open("bam_run_error.log", "w") as f:
        f.write(str(e))
