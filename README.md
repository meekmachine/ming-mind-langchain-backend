
## 明🧠🦜⛓️🍑
# Multi-Modal [M]ediator for [I]nterlocutive [N]oxiousness and [G]rievances 
## MING | an exploration of AI conflict mediation by The Knight Foundation School of Computing and Information Sciences at Florida International University.

This repository contains the FastAPI backend for MING, which integrates with LangChain to analyze text input and provide feedback.

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo-url.git
cd your-repo-directory
```

### 2. Environment Variables

Create a `.env` file in the root directory of the project and add the following:

```
OPENAI_API_KEY=your_openai_api_key
```

Replace `your_openai_api_key` with your actual OpenAI API key.

### 3. Install Dependencies

#### Using pip:

```bash
pip install -r requirements.txt
```

#### Using conda:

First, create a new conda environment:

```bash
conda create --name claridad-ai-env python=3.8
conda activate claridad-ai-env
```

Then, install the dependencies:

```bash
while read requirement; do conda install --yes $requirement; done < requirements.txt
```

## Running the Application

Activate the virtual environment (if using conda: `conda activate claridad-ai-env`), and then:

```bash
python app.py
```

The application will start, and you can access it at `http://localhost:5000`.

---

**Note**: Make sure to replace `your-repo-url` and `your-repo-directory` with the appropriate values for your project. Adjust the Python version in the conda setup if you're using a different version.