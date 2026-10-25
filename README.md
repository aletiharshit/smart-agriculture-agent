# 🌱 Smart Agriculture Agent

### AI-Based Decision Support for Smarter Farming

The **Smart Agriculture Agent** is a web-based application designed to help users assess basic farm conditions and receive actionable agricultural recommendations.

The application uses a rule-based reasoning approach to analyze soil moisture, temperature, crop type, and growth stage. It provides recommendations based on predefined rules and stores analysis records in an SQLite database.

🌐 **Live Demo:** https://smart-agriculture-agent-cse.streamlit.app/

---

## 📌 Problem Statement

Farmers need to make decisions about irrigation and crop care based on changing field conditions. Assessing these conditions and deciding on appropriate actions can be challenging without accessible decision-support tools.

This project demonstrates how an AI-based decision-support system can help interpret basic farm inputs and suggest appropriate actions.

## 🎯 Objectives

* Analyze basic agricultural conditions entered by the user.
* Apply rule-based reasoning to generate recommendations.
* Present understandable explanations for suggested actions.
* Store farm analysis records for historical reference.
* Demonstrate a practical application of AI concepts in agriculture.

## ✨ Features

* **Farm Monitoring:** Enter soil moisture, temperature, crop type, and growth stage.
* **Rule-Based AI Advisor:** Generate recommendations using predefined decision rules.
* **Explainable Recommendations:** Understand why a particular action is suggested.
* **Analysis History:** View previously recorded farm analyses.
* **Analytics Dashboard:** Explore historical analysis data.
* **SQLite Database:** Store farm readings and recommendation details.
* **Web Interface:** Access the application through a Streamlit-powered interface.

## 🛠️ Technologies Used

| Technology                | Purpose                                     |
| ------------------------- | ------------------------------------------- |
| Python                    | Core application logic                      |
| Streamlit                 | Web application interface                   |
| Pandas                    | Data handling and tabular analysis          |
| SQLite                    | Database for storing analysis records       |
| Rule-Based Reasoning      | Decision-making using predefined conditions |
| GitHub                    | Source code management                      |
| Streamlit Community Cloud | Web application deployment                  |

## ⚙️ How It Works

1. **Input:** The user enters basic farm conditions.
2. **Analysis:** The system evaluates the entered values using predefined rules.
3. **Reasoning:** The system determines which rules apply to the current conditions.
4. **Recommendation:** The application presents a suggested action and its reasoning.
5. **Storage:** The analysis and recommendation are saved in the SQLite database.
6. **Review:** Users can explore previous analyses through the application's history and analytics pages.

## 🧠 AI Technique

The project uses **rule-based reasoning**.

A rule-based system makes decisions using predefined conditions and corresponding actions.

For example, a simplified rule could be:

```text
IF soil moisture is below a configured threshold
THEN consider recommending irrigation.
```

The actual recommendation depends on the rules implemented in the project. Appropriate thresholds may vary with crop type, growth stage, soil characteristics, and local conditions.

The system is a rule-based prototype, not a machine-learning model. It does not independently learn from historical data.

## 🚀 Run the Project Locally

### Prerequisites

* Python installed on your computer
* Git (optional, for cloning the repository)
* An internet connection for the initial setup

### 1. Clone the repository

```bash
git clone https://github.com/aletiharshit/smart-agriculture-agent.git
```

### 2. Open the project directory

```bash
cd smart-agriculture-agent
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use the virtual environment's Python executable directly in the following steps.

### 5. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Run the application

```bash
python -m streamlit run app.py
```

Streamlit will provide a local address in the terminal. Open that address in your browser.

## 📁 Project Structure

```text
smart-agriculture-agent/
│
├── app.py             # Streamlit web application
├── database.py        # SQLite database operations
├── rules.py           # Rule-based recommendation logic
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

The SQLite database file is created locally when the application initializes the database.

## 🌍 Real-World Applications

* Basic agricultural decision support
* Irrigation awareness
* Farm-condition monitoring
* Educational demonstrations of AI in agriculture
* Prototyping explainable, rule-based agricultural systems

## ⚠️ Limitations

* Recommendations depend on predefined rules and user-provided inputs.
* The application does not automatically measure soil conditions using physical sensors.
* The current prototype does not independently learn from new data.
* Recommendations should not replace expert agricultural advice.
* Reliable crop-specific decisions require suitable agricultural data and locally validated thresholds.

## 🔮 Future Enhancements

* Integration with soil-moisture sensors and IoT devices
* Weather API integration
* More crop-specific recommendation rules
* Soil-type and rainfall information
* Integration with validated agricultural datasets
* Machine-learning-based analysis, if suitable training data becomes available
* More robust persistent database storage for the deployed application

## 👥 Team Members

1. **A Harshit** — 251FA04025
2. **A. Pallavitha** — 251FA04010
3. **A. Samhitha** — 251FA04001
4. **Ch. Hari Drakshayani** — 251FA04216

## 🎓 Project Information

**Project Title:** Smart Agriculture Agent
**Project Type:** AI Mini-Capstone Project
**Domain:** Artificial Intelligence in Agriculture
**Primary Technique:** Rule-Based Reasoning
**Programming Language:** Python

---

⭐ If you find this project interesting, feel free to explore the source code and live demonstration!
