from sentence_transformers import SentenceTransformer, util

# Inizializza il modello
model = SentenceTransformer('all-MiniLM-L6-v2')

# Email e query
emails = ["Domani abbiamo una riunione alle 10", "Hai visto il report?", "Grazie per la call"]
query = "incontro di lavoro"

# Embedding
email_embeddings = model.encode(emails, convert_to_tensor=True)
query_embedding = model.encode(query, convert_to_tensor=True)

# Calcola similarità
cosine_scores = util.cos_sim(query_embedding, email_embeddings)

# Ordina e mostra risultati
for i in range(len(emails)):
    print(f"Email: {emails[i]}")
    print(f"Similarità: {cosine_scores[0][i]:.4f}")
    print()