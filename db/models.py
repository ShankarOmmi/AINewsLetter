import uuid 
from db.database import get_connection, IS_POSTGRES

def add_subscriber(email:str):
    conn = get_connection()
    cursor = conn.cursor()

    token = str(uuid.uuid4())
    
    placeholder = "%s" if IS_POSTGRES else "?"
    try:
        cursor.execute(f"""
        INSERT INTO subscribers (email, unsubscribe_token)
        VALUES ({placeholder},{placeholder})
        """, (email, token))

        conn.commit()
        return {"success": True, "token" : token}
        
    except Exception as e:
        return {'success' : False, "error" : str(e)}

    finally:
        conn.close()

def get_subscriber_by_email(email:str):
    conn = get_connection()
    cursor = conn.cursor()
    
    placeholder = "%s" if IS_POSTGRES else "?"
    cursor.execute(f"SELECT * FROM subscribers WHERE email = {placeholder}", (email,))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def unsubscribe(token:str):
    conn = get_connection()
    cursor = conn.cursor()
    
    placeholder = "%s" if IS_POSTGRES else "?"
    cursor.execute(f"""
    UPDATE subscribers
    SET status = 'unsubscribed'
    WHERE unsubscribe_token = {placeholder}
    """, (token,))

    conn.commit()
    affected = cursor.rowcount
    conn.close()

    return affected>0



# -------------------------------
# SEND TRACKING
# -------------------------------
def log_send(edition_id, subject, total, status):
    conn = get_connection()
    cursor = conn.cursor()
    
    placeholder = "%s" if IS_POSTGRES else "?"
    cursor.execute(f"""
        INSERT INTO sends (edition_number, subject, total_recipients, status)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
    """, (
        edition_id,
        subject,
        total,
        status
    ))

    conn.commit()
    conn.close()



def get_active_subscribers():
    from db.database import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT email, unsubscribe_token
        FROM subscribers
        WHERE status = 'active'
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows
