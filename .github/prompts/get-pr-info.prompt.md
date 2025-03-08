# Generate Pull Request Title and Description

Follow these steps to generate a meaningful pull request title and description:

1. Check if you're on the develop branch:

    ```bash
    git --no-pager branch
    ```

2. Get the commit history since branching from main:

    ```bash
    git --no-pager log main..develop --no-merges --pretty=format:"%h %s%n%b" --reverse
    ```

3. Based on the commit history, generate a pull request:

    - **Title**: Should be a clear, concise summary of the changes
        - Start with a verb (Add, Update, Fix, etc.)
        - Keep it under 72 characters
        - Example: "Add user authentication system"

    - **Description**: Should include:
        - Summary of changes
        - Detailed list of major changes
        - Any breaking changes
        - Testing done
        - References to issues/tickets

Example PR format:
```md
Title: Add user authentication and dashboard features

Description:
This PR implements the core authentication system and dashboard features for the IoT device agent.

Changes:
- Implemented user authentication with Flask-Login
- Added dashboard with system information display
- Created settings management interface
- Implemented resource usage monitoring

Breaking Changes:
None

Testing:
- Verified login/logout functionality
- Tested system information display
- Validated settings management
- Confirmed resource monitoring accuracy

Related Issues:
Closes #123
```