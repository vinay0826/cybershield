Project Overview
Overview of the Project 

This is a Cyber Incident Monitoring System designed to detect and analyze cyber threats 
in real-time. It collects data from sources like Twitter (X) and news APIs, preprocesses it, 
analyzes it using ML and NLP techniques, and presents the results via a web dashboard. 
The system uses a combination of anomaly detection, sentiment analysis, and ML 
classification to identify potential cyber threats and generate alerts.

The project is structured into several components: 
• Backend: Handles data collection, preprocessing, analysis, and monitoring. 
• Frontend: Displays incidents and alerts via a dashboard. 
• Scripts: Initializes the database and populates it with test data. 
• Datasets: Used for training ML models and testing the system.


Steps to setup -

1. clone the git repository
2. install the venv using command:- python3 -m venv venv
3. activate the venv using command :- venv\Scripts\activate
4. intsall the requirements :- pip install -r requirements.txt
5. initialize the db :- python -m backend.database
6. now run the run_pipeline.bat file :- .\run_pipeline.bat
7. now your backend was initialized and running to access frontend - cd frontend and use live server in vs code or http server.


   Overview of the ML Component 
The ML part of this project is housed primarily in backend/analysis/ml_models.py. Its 
purpose is to classify text data (e.g., news articles, tweets) as either a "threat" 
(cybersecurity-related incident) or "benign" (non-threatening). Two ML algorithms are used: 
Random Forest (RF) and Support Vector Machine (SVM), though SVM is the one 
ultimately used for predictions. The system relies on a dataset 
(cybersecurity_training_data.csv) to train these models and a text vectorization 
technique called TF-IDF to convert text into a format the models can understand.



How the ML Algorithms Work 

Random Forest (RF) 
• Concept: Imagine 100 people (trees) voting on whether a text is a threat. Each 
person looks at different clues (TF-IDF scores) and decides based on rules they’ve 
learned (e.g., "if 'malware' > 0.5, it’s a threat"). 
• Training: 
 Each tree is trained on a random subset of the data and features. 
 Example: One tree might focus on "malware" and "attack", another on 
"phish" and "hack". 
• Prediction: Majority vote wins (not used here, but trained as a fallback). 

Support Vector Machine (SVM) 
• Concept: Picture a 2D graph with dots (texts) labeled "threat" or "benign". SVM 
draws the best straight line to separate them, maximizing the gap (margin) between 
the closest dots on either side. 
• In Reality: With TF-IDF, it’s not 2D but high-dimensional (e.g., 1000s of dimensions 
for all words). SVM finds a "hyperplane" instead of a line. 
• Training: 
o Learns which side of the hyperplane a text falls on based on its TF-IDF 
vector. 
o Example: "ransomware attack" (high "ransomware" score) falls on the 
"threat" side. 
• Prediction: 
o New text → TF-IDF vector → SVM checks which side of the hyperplane it’s on. 
o Probability: Measures how far it is from the hyperplane (farther = more 
confident). 

Example Walkthrough 
1. Training Data: 
a. "ransomware attack in kolkata", label=1 
b. "team lunch in kolkata", label=0 
c. TF-IDF: "ransomware" and "attack" get high scores for the first, "team" and 
"lunch" for the second.


2. Training:
   
a. SVM learns: High "ransomware" + "attack" = threat, high "team" + "lunch" = 
benign. 
4. New Text: "malware detected in pune" 
a. TF-IDF: High scores for "malware" and "detected". 
b. SVM: Predicts "threat" (1), confidence = 0.85. 
c. Database: Updates threat_label="threat", confidence_score=0.85. 
5. Alert: Confidence > 0.8 → alert triggered. 

Why These Algorithms? 
• Random Forest: Robust, handles noisy data well, but less interpretable with 
probabilities. 
• SVM: Excellent for text classification (sparse, high-dimensional data like TF-IDF), 
provides confidence scores, and is computationally efficient with a linear kernel.

Summary 
• Training: Uses cybersecurity_training_data.csv to teach RF and SVM what 
threats look like via TF-IDF features. 
• Prediction: SVM classifies new cleaned_text as "threat" or "benign" with 
confidence scores. 
• Integration: Drives real-time threat detection and alerting. 
• Process: Text → TF-IDF → SVM prediction → Database update → Alert if needed.
