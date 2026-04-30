from typing import Dict, Any


def render_report_ready_email(user_name: str, report_url: str, report_period: str) -> str:
    
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Report is Ready - Vellora</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #4DBF69 0%, #404CCF 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 300;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 18px;
            margin-bottom: 20px;
            color: #2c3e50;
        }}
        .message {{
            margin-bottom: 30px;
            font-size: 16px;
            color: #555;
        }}
        .report-info {{
            background-color: #f8f9fa;
            border-left: 4px solid #2E7D3E;
            padding: 20px;
            margin: 25px 0;
            border-radius: 0 5px 5px 0;
        }}
        .download-button {{
            display: inline-block;
            background: linear-gradient(135deg, #2E7D3E 0%, #1E3A8A 100%);
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            font-size: 16px;
            transition: transform 0.2s;
            margin: 20px 0;
        }}
        .download-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(46, 125, 62, 0.4);
        }}
        .footer {{
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 20px 30px;
            text-align: center;
            font-size: 14px;
        }}
        .footer p {{
            margin: 0;
        }}
        .note {{
            font-size: 14px;
            color: #7f8c8d;
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header" style="background: linear-gradient(135deg, #2E7D3E 0%, #1E3A8A 100%); color: white; padding: 30px; text-align: center;">
            <div style="margin-bottom: 15px;">
                <img src="https://i.imgur.com/e7U6gC7.png" alt="Vellora Logo" style="height: 45px; width: auto; display: inline-block; max-width: 180px; object-fit: contain;" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline-block';">
                <span style="display: none; background: rgba(255,255,255,0.15); padding: 10px 20px; border-radius: 12px; font-size: 20px; font-weight: bold; letter-spacing: 2px; color: white; border: 2px solid rgba(255,255,255,0.3); text-shadow: 1px 1px 2px rgba(0,0,0,0.2); font-family: 'Arial', sans-serif;">
                    VELLORA
                </span>
            </div>
            <p style="color: white; margin: 10px 0 0 0;">Your expense report is ready!</p>
        </div>
        
        <div class="content">
            <div class="greeting">
                Hello {user_name}!
            </div>
            
            <div class="message">
                Great news! Your expense report has been successfully generated and is ready for download.
            </div>
            
            <div class="report-info">
                <strong>Report Period:</strong> {report_period}<br>
                <strong>Generated:</strong> Just now<br>
                <strong>Status:</strong> Ready for download
            </div>
            
            <center>
                <a href="{report_url}" class="download-button" style="display: inline-block; background: linear-gradient(135deg, #2E7D3E 0%, #1E3A8A 100%); color: white !important; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">
                    Download Your Report
                </a>
            </center>
            
            <div class="note">
                <strong>Note:</strong> This download link will be available for 90 days. Make sure to download your report before it expires.
            </div>
        </div>
        
        <div class="footer">
            <p>© 2025 Vellora</p>
        </div>
    </div>
</body>
</html>"""
    
    return html_template.format(
        user_name=user_name,
        report_url=report_url,
        report_period=report_period
    )


def render_report_ready_text(user_name: str, report_url: str, report_period: str) -> str:
    
    return f"""
Hello {user_name}!

Your Vellora expense report is ready for download.

Report Details:
- Period: {report_period}
- Generated: Just now
- Status: Ready for download

Download your report here: {report_url}

Note: This download link will be available for 90 days.

---
Vellora 
    """.strip()


def render_report_failed_email(user_name: str, report_period: str, retry_url: str) -> str:
    
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Report Generation Issue - Vellora</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #4DBF69 0%, #404CCF 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 300;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .greeting {{
            font-size: 18px;
            margin-bottom: 20px;
            color: #2c3e50;
        }}
        .message {{
            margin-bottom: 30px;
            font-size: 16px;
            color: #555;
        }}
        .report-info {{
            background-color: #fff5f5;
            border-left: 4px solid #e74c3c;
            padding: 20px;
            margin: 25px 0;
            border-radius: 0 5px 5px 0;
        }}
        .retry-button {{
            display: inline-block;
            background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            font-size: 16px;
            transition: transform 0.2s;
            margin: 20px 0;
        }}
        .retry-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(39, 174, 96, 0.3);
        }}
        .footer {{
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 20px 30px;
            text-align: center;
            font-size: 14px;
        }}
        .footer p {{
            margin: 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header" style="background: linear-gradient(135deg, #2E7D3E 0%, #1E3A8A 100%); color: white; padding: 30px; text-align: center;">
            <div style="margin-bottom: 15px;">
                <img src="https://i.imgur.com/e7U6gC7.png" alt="Vellora Logo" style="height: 45px; width: auto; display: inline-block; max-width: 180px; object-fit: contain;" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline-block';">
                <span style="display: none; background: rgba(255,255,255,0.15); padding: 10px 20px; border-radius: 12px; font-size: 20px; font-weight: bold; letter-spacing: 2px; color: white; border: 2px solid rgba(255,255,255,0.3); text-shadow: 1px 1px 2px rgba(0,0,0,0.2); font-family: 'Arial', sans-serif;">
                    VELLORA
                </span>
            </div>
            <p style="color: white; margin: 10px 0 0 0;">Report generation encountered an issue</p>
        </div>
        
        <div class="content">
            <div class="greeting">
                Hello {user_name},
            </div>
            
            <div class="message">
                We encountered an issue while generating your expense report. Don't worry - we can try again!
            </div>
            
            <div class="report-info">
                <strong>Report Period:</strong> {report_period}<br>
                <strong>Status:</strong> Generation failed<br>
                <strong>Next Step:</strong> Click below to retry
            </div>
            
            <center>
                <a href="{retry_url}" class="retry-button" style="display: inline-block; background: linear-gradient(135deg, #2E7D3E 0%, #1E3A8A 100%); color: white !important; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">
                    Retry Report Generation
                </a>
            </center>
            
        </div>
        
        <div class="footer">
            <p>© 2025 Vellora</p>
        </div>
    </div>
</body>
</html>"""
    
    return html_template.format(
        user_name=user_name,
        report_period=report_period,
        retry_url=retry_url
    )