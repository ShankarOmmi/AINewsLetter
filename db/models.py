import uuid 
from db.database import get_connection

def add_subscriber(email:str):
    conn = get_connection()
    cursor = conn.cursor()

    token = str(uuid.uuid4())

    try:
        cursor.execute("""
        INSERT INTO subscribers (email, unsubscribe_token)
        VALUES (?,?)
        """, (email, token))

        conn.commit ()
        return {"success": True, "token" : token}
        
    except Exception as e:
        return {'success' : False, "error" : str(e)}

    finally:
        conn.close()

def get_subscriber_by_email(email:str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM subscribers WHERE email - ?", (email,))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def unsubscribe(token:str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE subscribers
    SET status = 'unsubscribed'
    WHERE unsubscribe_token = ?
    """, (token,))

    conn.commit()
    affected = cursor.rowcount
    conn.close()

    return affected>0

def get_active_subscribers():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor = conn.execute("""
    SELECT * FROM subscribers 
    WHERE status = 'active'
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

def log_send(edition_number, subject, total_recipients, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO sends (edition number, sunject, total_recipients, status)
    VALUES (?,?,?,?)
    """, (edition_number, subject, total_recipients, status))

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