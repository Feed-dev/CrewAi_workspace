from datetime import datetime
import pytz


def update_readme():
    # Read the current README
    with open('README.md', 'r') as file:
        lines = file.readlines()

    # Get current date in UTC
    current_date = datetime.now(pytz.UTC).strftime("%Y-%m-%d")

    # Update first line
    lines[0] = f"Last Updated: {current_date}\n"

    # Write back to README
    with open('README.md', 'w') as file:
        file.writelines(lines)


if __name__ == "__main__":
    update_readme()
