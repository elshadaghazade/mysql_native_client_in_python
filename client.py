from socket import *
import inquirer
from modules.mysql import MySQL
from dotenv import load_dotenv
from terminaltables import AsciiTable
import os

def ask():
    load_dotenv()

    mysql_host = os.environ['MYSQL_HOST'] if 'MYSQL_HOST' in os.environ else None
    mysql_port = os.environ['MYSQL_PORT'] if 'MYSQL_PORT' in os.environ else None
    mysql_user = os.environ['MYSQL_USER'] if 'MYSQL_USER' in os.environ else None
    mysql_pass = os.environ['MYSQL_PASS'] if 'MYSQL_PASS' in os.environ else None

    questions = [
        inquirer.Text("mysql_host", message="Enter MySQL host", validate=lambda _, x: x.strip(), default=mysql_host),
        inquirer.Text("mysql_port", message="Enter MySQL port", validate=lambda _, x: x.strip(), default=mysql_port),
        inquirer.Text("mysql_user", message="Enter MySQL user", validate=lambda _, x: x.strip(), default=mysql_user),
        inquirer.Password("mysql_password", message="Enter MySQL password", default=mysql_pass)
    ]

    answers = inquirer.prompt(questions)

    with MySQL(host=answers['mysql_host'], port=answers['mysql_port'], user=answers['mysql_user'], password=answers['mysql_password']) as mysql:
        try:
            handshake_package = mysql.connect()
            info = handshake_package.parse()
            
            if not mysql.login(handshake_package, info['package_number']+1):
                print("Could not login. Try again!")
            else:
                print("You are welcome!")
                print(f"Server version: MySQL {info['server_version']}")
                print(f"Connection ID: {info['connection_id']}")
                print(f"Server Language: {info['server_language']}")
                print("Fetching databases...")
                resp = mysql.show_databases()

                questions = [
                    inquirer.List('db', message="Choose database", choices=[x['text'] for x in resp['databases']])
                ]
                answers = inquirer.prompt(questions)
                print(f"Switching to {answers['db']} database...")
                mysql.init_db(answers['db'])
                print("Done")
                query = input("Techacademy.az CLI >> ")
                while query.lower() != 'q':
                    resp = mysql.query(query)
                    if resp['package_name'] == 'OK_PACKAGE':
                        print("Done.", f"affected rows: {resp['affected_rows']}")
                    elif resp['package_name'] == 'ERR_PACKAGE':
                        print("MySQL Server Error. ", f"{resp['error_code']} - {resp['error_message']}")
                    elif resp['package_name'] == 'EOF_PACKAGE':
                        print("EOF")
                    elif resp['package_name'] == 'QUERY_RESPONSE_PACKAGE':
                        table_data = [
                            [f"{x['name']}({x['length']})" for x in resp['fields']]
                        ]

                        for i in resp['rows']:
                            table_data.append(i)

                        table = AsciiTable(table_data)
                        print(table.table)
                    else:
                        print("unknown response")
                    query = input("Techacademy.az CLI >> ")
                    
        except Exception as err:
            print(err)

if __name__ == "__main__":
    ask()