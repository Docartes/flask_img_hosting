from flask import Flask, request, jsonify, render_template, make_response, send_file
import psycopg2 
from dotenv import load_dotenv
import base64
import json
import io
import os

load_dotenv()

app = Flask(__name__)
host = os.getenv('host')

@app.route("/")
def home():
	return render_template('index.html')

@app.route("/images")
def get_images():
	try:
		conn = psycopg2.connect(os.getenv('database_url'))
		cur = conn.cursor()
		query = "SELECT * FROM images_table"
		cur.execute(query)
		data = cur.fetchall()
		conn.commit()
		cur.close()

		result = []
		for d in data:
			# img_bin = d[1]
			# img_data = base64.b64encode(img_bin).decode('utf-8')
			result.append({
				'id': d[0],
				'link': f'{host}/image/{d[0]}',
				'created_at': d[2]
			})

		return jsonify(result), 200
	except Exception as e:
		return jsonify({'error': str(e)}), 400

@app.route("/image/<id>", methods=['GET'])
def get_image_by_id(id):
	try:
		conn = psycopg2.connect(os.getenv('database_url'))
		cur = conn.cursor()
		query = "SELECT * FROM images_table WHERE id = %s"
		cur.execute(query, (id, ))
		data = cur.fetchall()
		conn.commit()
		cur.close()

		img_bin = data[0][1]

		png = 'png'
		jpeg = 'jpeg'

		res = send_file(io.BytesIO(img_bin), mimetype=f"image/{png or jpeg}")
		if res.headers.set('Content-Type', 'image/jpeg'):
			res.headers.set('Content-Type', 'image/jpeg')
			res.headers.set('Content-Disposition', 'inline', filename=f'images_table_{id}.jpg')

		if res.headers.set('Content-Type', 'image/png'):
			res.headers.set('Content-Type', 'image/png')
			res.headers.set('Content-Disposition', 'inline', filename=f'images_table_{id}.png')

		return res
	except Exception as e:
		return jsonify({'error': str(e)}), 400


@app.route('/upload_image', methods=['POST'])
def upload_image():
	try:
		image_data = request.files['image']

		conn = psycopg2.connect(os.getenv('database_url'))
		cur = conn.cursor()
		query = "INSERT INTO images_table (image) VALUES (%s)"
		cur.execute(query, (image_data.read(),))
		query_select = "SELECT * FROM images_table ORDER BY created_at DESC"
		cur.execute(query_select)
		img_data = cur.fetchone()
		conn.commit()
		cur.close()

		return jsonify({'link': f'{host}/image/{img_data[0]}'}), 200

	except Exception as e:
		return jsonify({'error': str(e)}), 400

@app.route('/delete_image/<id>', methods=['DELETE'])
def remove(id):
	try:
		conn = psycopg2.connect(os.getenv('database_url'))
		cur = conn.cursor()
		query = "DELETE FROM images_table WHERE id = (%s)"
		cur.execute(query, (id,))
		conn.commit()
		cur.close()

		return jsonify({'message': f'Delete image with id = {id} success'}), 200
		
	except Exception as e:
		return jsonify({'error': str(e)}), 400


if __name__ == "__main__":
	app.run(debug=True)