請遵循以下流程檢查並設定開發環境。

please do git commit for each step when you run command of edit files. If nothing to commit, just ignore it.

1. Make sure the working tree is clean.

    ```bash
    git status
    ```

    If the working directory is not clean, please stop execution.

2. Check for python environment. It must be larger than `3.12.0`.

    ```bash
    python --version
    ```

3. Install pdm.

    ```bash
    pip install pdm
    ```

4. Initialize pdm.

    ```bash
    pdm init
    ```

Let's do this step by step.
