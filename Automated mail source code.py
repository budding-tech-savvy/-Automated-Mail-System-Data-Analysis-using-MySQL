import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import sqlite3

data=pd.read_csv('/config/workspace/sql .csv')
# Read the CSV file into a pandas DataFrame

# Create an in-memory SQLite database
conn = sqlite3.connect(':memory:')

# Store the DataFrame in the SQLite database
data.to_sql('data', conn, index=False)

# Define your SQL query
query = """
with cte as (Select jobtitle,employeename,totalpaybenefits ,
row_number() over(partition by jobtitle order by totalpaybenefits desc) as ranking
from data)

,cte1 as (select jobtitle,employeename,totalpaybenefits,ranking from cte 
where ranking=1 or ranking=2)

select jobtitle,max(case when ranking=1 then employeename end) as best_salary,
max(case when ranking=2 then employeename else null end) as second_best_salary
from cte1 
group by jobtitle
"""

# Execute the SQL query
result = pd.read_sql_query(query, conn)
# Print the result

email_content = result.to_html()  # Convert DataFrame to HTML for email body
additional_lines = """
<p>Good Morning Team !</p>
<p>Kindly get the best paid employees and second best paid employees as per job titles</p>
"""

# Concatenate the additional lines with the DataFrame HTML content
email_content = additional_lines + email_content

sender_email = 'guptaraghu386@gmail.com'  # Your email
receiver_email = 'manujsinghwal2060@gmail.com'  # Recipient's email
password = 'svzrfgvpxkjqlejt'  # Your email password

# Compose email message
msg = MIMEText(email_content, 'html')
msg['Subject'] = 'Best Paid City Employees'
msg['From'] = sender_email
msg['To'] = receiver_email

# Connect to the SMTP server and send the email
try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
finally:
    server.quit()
