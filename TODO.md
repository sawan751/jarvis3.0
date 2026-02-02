# TODO: Implement Opening Other Software

## Tasks
- [x] Update app_map in open_application function to include Instagram, Telegram, YouTube, and fix WhatsApp executable name
- [x] Update app_map in close_application function with the same entries
- [x] Update app_map in launch_program function with the same entries
- [x] Modify open_application function to handle web URLs (if exe starts with 'http', use webbrowser.open)
- [x] Modify launch_program function similarly for web URLs
- [x] Test the changes (run the app and try opening the apps)

## Notes
- For web-based apps like Instagram, Telegram, YouTube, open their URLs in the browser if no desktop app is found.
- WhatsApp: Changed mapping to web URL to fix opening issue.
- Add logic to detect web URLs and open in browser.
