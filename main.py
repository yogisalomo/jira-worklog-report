import requests
import json
import datetime

jira_base_url = ""
jira_api_token = ""


def generate_message():
    today = datetime.date.today()
    today_date = today.strftime("%Y-%m-%d")
    url = "%s/rest/api" \
          "/2/search?jql=worklogDate=%s&fields=worklog&orderBy=worklogAuthor" % (jira_base_url, today_date)
    headers = {
        "content-type": "application/json",
        "Authorization": "Basic %s" % jira_api_token,
    }
    response = requests.get(url, headers=headers)
    contents = json.loads(response.text)
    report_by_employee = {}
    for issue in contents["issues"]:
        work_log_list = issue["fields"]["worklog"]["worklogs"]
        for work_log in work_log_list:
            # Because the JQL also loads the previous work log on an issue that have today's work log
            # Check only those that are logged today by comparing its started attribute
            if today_date in work_log["started"]:
                author_name = work_log["author"]["name"]
                report_content = "%s: %s" % (work_log["timeSpent"], work_log["comment"])
                if author_name in report_by_employee:
                    report_by_employee[author_name] += "\n%s" % report_content
                else:
                    report_by_employee[author_name] = report_content

    # Append each employee's report to a string
    slack_message = ""
    for employee in report_by_employee:
        slack_message += "%s:\n" % employee
        slack_message += "%s\n\n" % report_by_employee[employee]
    return slack_message


def main():
    slack_message = generate_message()
    print(slack_message)


main()