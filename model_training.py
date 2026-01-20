import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import pickle
import string
import sys
import io

# Fix encoding issues for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def preprocess_text(text):
    """Preprocess text data"""
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = ' '.join(text.split())
    return text

def create_training_data():
    """Create comprehensive training dataset"""
    spam_messages = [
        "WINNER! You have won a £1000 cash prize! Call now!",
        "Free entry in 2 a wkly comp to win FA Cup final tkts",
        "Urgent! You have won a lottery of $1 million dollars",
        "Congratulations! You have been selected for a special prize",
        "Click here to claim your free iPhone 15 Pro Max now!",
        "FREE GIFT! Reply YES to claim your reward immediately",
        "You have been approved for a credit card with $50000 limit",
        "Act now! Limited time offer expires in 24 hours",
        "Claim your tax refund of $5000 immediately",
        "Win a luxury vacation to Hawaii! Click here now",
        "Your account has been compromised. Verify now to avoid suspension",
        "Get rich quick! Earn $10000 per week from home",
        "Lose 20 pounds in 2 weeks! Buy our miracle pills now",
        "Hot singles in your area want to meet you",
        "You've been selected for a government grant of $25000",
        "Make money fast with this one weird trick",
        "Congratulations! You've won an all-expenses-paid cruise",
        "Final notice: Your vehicle warranty is about to expire",
        "Refinance your mortgage and save thousands monthly",
        "Your Amazon order has been cancelled. Click to resolve",
        "IRS: You owe back taxes. Pay now to avoid arrest",
        "Nigerian prince needs your help transferring $50 million",
        "Work from home and earn $5000 weekly guaranteed",
        "Free trial - no credit card required! Sign up now",
        "You have unclaimed inheritance of €500000",
        "Buy cheap watches - Rolex replicas at 95% off",
        "Your computer has a virus! Download antivirus now",
        "Congratulations! You are the 1000000th visitor. Claim prize",
        "Get out of debt fast! We can help you today",
        "Hot stock tip! This will triple your investment",
        "Miracle weight loss - lose 30 lbs in 30 days",
        "Cash advance approved! Get $3000 in your account today",
        "Your PayPal account is locked. Verify identity now",
        "Free ringtones! Text YES to 12345 to download",
        "You qualify for a $250000 loan at 0% interest",
        "Hot deal! Brand new iPhone for only $99",
        "Your email has won in our sweepstakes drawing",
        "Mystery shopper needed. Earn $300 per day",
        "Exclusive offer! Get paid to take surveys online",
        "Limited time: 90% off designer handbags!"
    ]
    
    ham_messages = [
        "Hey, are we still meeting tomorrow at 3 PM?",
        "Can you pick up some milk on your way home?",
        "Meeting scheduled for 3 PM in conference room B",
        "Please review the attached document and provide feedback",
        "Dinner at 7? Let me know if you can make it",
        "The project deadline has been extended to next Friday",
        "Happy birthday! Hope you have a wonderful day",
        "Thanks for your help with the presentation today",
        "Can you send me the report by end of day?",
        "See you at the gym tomorrow morning at 6 AM",
        "Mom called. She wants you to call her back",
        "The meeting notes are in the shared drive",
        "Don't forget to bring your laptop to the workshop",
        "Great job on the presentation! The client loved it",
        "Can we reschedule our 2 PM meeting to 4 PM?",
        "Your package has been delivered to the front door",
        "Reminder: dentist appointment on Wednesday at 10 AM",
        "The report looks good. Just a few minor edits needed",
        "Traffic is terrible. I'll be 15 minutes late",
        "Coffee break in 10 minutes at the cafeteria",
        "Your flight is confirmed for next Monday at 8 AM",
        "Please RSVP for the team lunch by Friday",
        "The software update is scheduled for tonight",
        "Your prescription is ready for pickup at the pharmacy",
        "Team meeting moved to Conference Room A",
        "Can you review this code before I push it?",
        "Lunch was great! Thanks for the recommendation",
        "Your library books are due next week",
        "The kids have a soccer game on Saturday at 10",
        "Don't forget we have plans this weekend",
        "Your order has been shipped. Track it here",
        "The wifi password is on the whiteboard",
        "Please submit your timesheet by Friday",
        "Your reservation is confirmed for 8 people at 7 PM",
        "The presentation files are in the project folder",
        "Can you help me with this Excel formula?",
        "Your subscription renewal is coming up next month",
        "The printer is out of paper on the second floor",
        "Your appointment has been confirmed for next Tuesday",
        "Thanks for attending today's training session"
    ]
    
    data = {
        'message': spam_messages + ham_messages,
        'label': ['spam'] * len(spam_messages) + ['ham'] * len(ham_messages)
    }
    
    return pd.DataFrame(data)

def train_model():
    """Train the spam detection model"""
    print("=" * 60)
    print("SPAM EMAIL DETECTION MODEL TRAINING")
    print("=" * 60)
    
    print("\n[1/6] Creating training dataset...")
    df = create_training_data()
    print(f"[SUCCESS] Dataset created: {len(df)} messages")
    print(f"  - Spam messages: {len(df[df['label'] == 'spam'])}")
    print(f"  - Ham messages: {len(df[df['label'] == 'ham'])}")
    
    print("\n[2/6] Preprocessing text data...")
    df['processed'] = df['message'].apply(preprocess_text)
    print("[SUCCESS] Text preprocessing complete")
    
    print("\n[3/6] Splitting dataset (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        df['processed'], df['label'], test_size=0.2, random_state=42, stratify=df['label']
    )
    print(f"[SUCCESS] Training set: {len(X_train)} messages")
    print(f"[SUCCESS] Test set: {len(X_test)} messages")
    
    print("\n[4/6] Creating feature vectors (CountVectorizer)...")
    vectorizer = CountVectorizer(max_features=3000, stop_words='english')
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    print(f"[SUCCESS] Vocabulary size: {len(vectorizer.vocabulary_)} words")
    print(f"[SUCCESS] Feature matrix shape: {X_train_vec.shape}")
    
    print("\n[5/6] Training Multinomial Naive Bayes classifier...")
    model = MultinomialNB()
    model.fit(X_train_vec, y_train)
    print("[SUCCESS] Model training complete")
    
    print("\n[6/6] Evaluating model performance...")
    y_pred = model.predict(X_test_vec)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, pos_label='spam')
    recall = recall_score(y_test, y_pred, pos_label='spam')
    f1 = f1_score(y_test, y_pred, pos_label='spam')
    
    print("\n" + "=" * 60)
    print("MODEL PERFORMANCE METRICS")
    print("=" * 60)
    print(f"Accuracy:  {accuracy * 100:.2f}%")
    print(f"Precision: {precision * 100:.2f}%")
    print(f"Recall:    {recall * 100:.2f}%")
    print(f"F1-Score:  {f1 * 100:.2f}%")
    
    cm = confusion_matrix(y_test, y_pred, labels=['ham', 'spam'])
    print("\nConfusion Matrix:")
    print("                 Predicted")
    print("                Ham    Spam")
    print(f"Actual Ham      {cm[0][0]:3d}     {cm[0][1]:3d}")
    print(f"       Spam     {cm[1][0]:3d}     {cm[1][1]:3d}")
    
    print("\n" + "=" * 60)
    print("SAVING MODEL FILES")
    print("=" * 60)
    
    with open('spam_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("[SUCCESS] Model saved: spam_model.pkl")
    
    with open('vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    print("[SUCCESS] Vectorizer saved: vectorizer.pkl")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] TRAINING COMPLETE!")
    print("=" * 60)
    print("\nYou can now run the Flask application:")
    print("  python app.py")
    print("\nThen open your browser to: http://127.0.0.1:8080")
    print("=" * 60)
    
    return model, vectorizer

if __name__ == '__main__':
    train_model()