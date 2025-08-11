import json
import os
import pymysql

# 환경 변수에서 DB 접속 정보 읽기
db_host = os.environ.get('DB_HOST')
db_user = os.environ.get('DB_USER')
db_pass = os.environ.get('DB_PASS')
db_name = os.environ.get('DB_NAME')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
    except Exception:
        return {
            'statusCode': 400,
            'body': json.dumps({'success': False, 'message': 'Invalid JSON'})
        }

    username = body.get('username')
    if not username:
        return {
            'statusCode': 400,
            'body': json.dumps({'success': False, 'message': 'Username required'})
        }

    conn = None
    try:
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )

        with conn.cursor() as cursor:
            # 현재 beans, coupon 조회
            sql = "SELECT beans, coupon FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            user = cursor.fetchone()
            if user is None:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'success': False, 'message': 'User not found'})
                }

            beans = user['beans'] + 1
            coupon = user['coupon']
            reset = False

            if beans >= 10:
                beans = 0
                coupon += 1
                reset = True

            # 업데이트
            update_sql = "UPDATE users SET beans = %s, coupon = %s WHERE username = %s"
            cursor.execute(update_sql, (beans, coupon, username))

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'total_beans': beans,
                'coupon': coupon,
                'reset': reset
            })
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'success': False, 'message': 'Internal server error'})
        }
    finally:
        if conn:
            conn.close()
