# AI-Docking-1

A tool for AI-assisted molecular docking.

## Installation

### Setup for Backend

1. Clone the repository:
    ```bash
    git clone git@github.com:piyushjha0409/ai-docking-1.git
    cd ai-docking-1/backend
    ```

2. Create a virtual environment:
    ```bash
    python -m venv .venv
    ```
    or
    ```bash
    python3 -m venv .venv
    ```

3. Activate the virtual environment:
    - On Windows:
      ```bash
      .venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      source .venv/bin/activate
      ```

4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

5. Run the main script:
    ```bash
    uvicorn main:app --reload
    ```