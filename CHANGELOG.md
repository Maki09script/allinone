# Changelog

## [1.0.0] - 2026-01-20
### Added
- **All-In-One License System**: Secure login system with HWID locking.
- **Discord Bot**: Admin commands `/getkey`, `/resethwid`, `/deletekey`.
- **License Server**: Flask API with replay protection and rate limiting.
- **Security**: HMAC-SHA256 request signing for all API calls.
- **Streammode**: "Privacy Mode" in Cleaner GUI to hide sensitive usernames.
- **Robustness**: Improved BAM cleaner and file deletion logic to prevent crashes.
- **Documentation**: User Guide, Admin Guide, and Deployment Guide.

### Fixed
- **BAM Cleaner**: Now runs silently without console popups.
- **License Expiry**: Timed keys now start counting down only after first activation.
- **Login Crash**: Fixed application crash when transitioning from Login to Main App.
