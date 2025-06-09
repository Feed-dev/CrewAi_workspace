from datetime import datetime
import pytz
import os


def update_readme():
    try:
        # Try reading with different encodings
        encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'latin-1']

        for encoding in encodings:
            try:
                with open('README.md', 'r', encoding=encoding) as file:
                    lines = file.readlines()
                break
            except UnicodeDecodeError:
                continue
            except FileNotFoundError:
                # Create file if it doesn't exist
                lines = ["Last Updated: \n"]
                break

        # Get current date in UTC
        current_date = datetime.now(pytz.UTC).strftime("%Y-%m-%d")

        # Update first line
        lines[0] = f"Last Updated: {current_date}\n"

        # Write with UTF-8 encoding
        with open('README.md', 'w', encoding='utf-8') as file:
            file.writelines(lines)

    except Exception as e:
        print(f"Error updating README: {str(e)}")
        raise


if __name__ == "__main__":
    update_readme()
