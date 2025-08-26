import imaplib
import email

# Gmail IMAP server details
IMAP_SERVER = "imap.gmail.com"
EMAIL_ACCOUNT = "percy@randallsstore.com.au"
APP_PASSWORD = "tfaf libd uqws rtwv"  # 16-char app password, not your normal password

mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL_ACCOUNT, APP_PASSWORD)

mail.select("inbox")

status, data = mail.search(None, "ALL")
mail_ids = data[0].split()

latest_email_id = mail_ids[-1]
status, data = mail.fetch(latest_email_id, "(RFC822)")

raw_email = data[0][1]
msg = email.message_from_bytes(raw_email)

print("From:", msg["From"])
print("Subject:", msg["Subject"])
