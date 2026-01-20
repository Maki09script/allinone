import cleaner
import time

def mock_callback(msg):
    print(f"[GUI LOG] {msg}")

print("Testing BAM Cleaner Logging...")
cleaner.clean_bam_state(log_callback=mock_callback)
print("Test Complete.")
