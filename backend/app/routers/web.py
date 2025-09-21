from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def index_page():
	return """
	<!doctype html>
	<html>
	<head>
		<meta charset=\"utf-8\" />
		<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
		<title>Authenticity Validator</title>
		<style>
			body{font-family:system-ui,Segoe UI,Arial;margin:24px;max-width:900px}
			.card{border:1px solid #ddd;padding:16px;border-radius:8px;margin-bottom:16px}
			label{display:block;margin:8px 0 4px}
			button{padding:8px 14px;border:1px solid #0a66c2;background:#0a66c2;color:#fff;border-radius:6px;cursor:pointer}
			pre{white-space:pre-wrap;background:#f6f8fa;padding:12px;border-radius:6px}
		</style>
	</head>
	<body>
		<h2>Certificate Verification</h2>
		<div class=\"card\">
			<form id=\"verifyForm\">
				<label>Certificate file (image/PDF)</label>
				<input type=\"file\" name=\"file\" required />
				<label>Institution ID (optional)</label>
				<input type=\"text\" name=\"institution_id\" placeholder=\"UoJ-01\" />
				<div style=\"margin-top:12px\"><button type=\"submit\">Verify</button></div>
			</form>
		</div>
		<div class=\"card\">
			<h3>Result</h3>
			<pre id=\"result\">Submit a file to see results</pre>
		</div>

		<script>
		const form = document.getElementById('verifyForm');
		const result = document.getElementById('result');
		form.addEventListener('submit', async (e) => {
			e.preventDefault();
			const data = new FormData(form);
			result.textContent = 'Verifying...';
			try {
				const res = await fetch('/verify/upload', { method: 'POST', body: data });
				const json = await res.json();
				result.textContent = JSON.stringify(json, null, 2);
			} catch (err) {
				result.textContent = 'Error: ' + (err?.message || err);
			}
		});
		</script>
	</body>
	</html>
	"""


@router.get("/v/{certificate_id}", response_class=HTMLResponse)
def user_verify_page(certificate_id: str):
	return f"""
	<!doctype html>
	<html>
	<head>
		<meta charset=\"utf-8\" />
		<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
		<title>Verify Certificate {certificate_id}</title>
		<style>body{{font-family:system-ui,Segoe UI,Arial;margin:24px;max-width:800px}}</style>
	</head>
	<body>
		<h2>Verification Result</h2>
		<pre id=\"out\">Loading...</pre>
		<script>
		(async () => {{
			try {{
				const res = await fetch('/institutions/UoJ-01/records/{certificate_id}');
				if (res.ok) {{
					const json = await res.json();
					document.getElementById('out').textContent = JSON.stringify(json, null, 2);
				}} else {{
					document.getElementById('out').textContent = 'Not found';
				}}
			}} catch(e) {{
				document.getElementById('out').textContent = 'Error: ' + (e?.message||e);
			}}
		}})();
		</script>
	</body>
	</html>
	"""

@router.get("/admin-ui", response_class=HTMLResponse)
def admin_page():
	return """
	<!doctype html>
	<html>
	<head>
		<meta charset=\"utf-8\" />
		<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
		<title>Admin - Authenticity Validator</title>
		<style>
			body{font-family:system-ui,Segoe UI,Arial;margin:24px;max-width:900px}
			.card{border:1px solid #ddd;padding:16px;border-radius:8px;margin-bottom:16px}
			label{display:block;margin:8px 0 4px}
			button{padding:8px 14px;border:1px solid #0a66c2;background:#0a66c2;color:#fff;border-radius:6px;cursor:pointer}
			pre{white-space:pre-wrap;background:#f6f8fa;padding:12px;border-radius:6px}
			input[type=text],input[type=password]{width:100%;max-width:360px;padding:8px;border:1px solid #ccc;border-radius:6px}
		</style>
	</head>
	<body>
		<h2>Admin Console</h2>
		<div class=\"card\">
			<h3>Login</h3>
			<label>Username</label>
			<input id=\"username\" type=\"text\" placeholder=\"admin\" />
			<label>Password</label>
			<input id=\"password\" type=\"password\" placeholder=\"admin123\" />
			<div style=\"margin-top:12px\"><button id=\"loginBtn\">Login</button></div>
		</div>

		<div class=\"card\">
			<h3>Bulk Upload Certificates (CSV)</h3>
			<input id=\"csv\" type=\"file\" accept=\".csv\" />
			<div style=\"margin-top:12px\"><button id=\"uploadBtn\">Upload</button></div>
		</div>

		<div class=\"card\">
			<h3>Stats</h3>
			<div><button id=\"statsBtn\">Refresh</button></div>
			<pre id=\"stats\">No data</pre>
			<canvas id=\"chart\" width=\"600\" height=\"200\"></canvas>
		</div>

		<script>
		let token = localStorage.getItem('token') || '';
		const loginBtn = document.getElementById('loginBtn');
		const uploadBtn = document.getElementById('uploadBtn');
		const statsBtn = document.getElementById('statsBtn');
		const stats = document.getElementById('stats');

		loginBtn.onclick = async () => {
			const username = document.getElementById('username').value;
			const password = document.getElementById('password').value;
			const data = new URLSearchParams();
			data.append('username', username);
			data.append('password', password);
			data.append('grant_type', 'password');
			const res = await fetch('/admin/login', { method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body: data });
			const json = await res.json();
			token = json.access_token || '';
			localStorage.setItem('token', token);
			alert(token ? 'Logged in' : 'Login failed');
		};

		uploadBtn.onclick = async () => {
			const f = document.getElementById('csv').files[0];
			if(!f){ return alert('Choose a CSV file'); }
			const fd = new FormData();
			fd.append('file', f);
			const res = await fetch('/admin/bulk-upload', { method:'POST', headers: { 'Authorization': 'Bearer ' + token }, body: fd });
			const json = await res.json();
			alert(JSON.stringify(json));
		};

		function drawChart(success, failure){
			const c = document.getElementById('chart');
			if(!c) return; const ctx = c.getContext('2d');
			ctx.clearRect(0,0,c.width,c.height);
			const total = success + failure || 1;
			const sx = (success/total) * c.width;
			const fx = (failure/total) * c.width;
			ctx.fillStyle = '#2da44e'; ctx.fillRect(0,0,sx,50);
			ctx.fillStyle = '#d1242f'; ctx.fillRect(sx,0,fx,50);
			ctx.fillStyle = '#000'; ctx.fillText('Success: '+success, 10, 70);
			ctx.fillText('Failure: '+failure, 120, 70);
		}

		statsBtn.onclick = async () => {
			const res = await fetch('/admin/stats', { headers: { 'Authorization': 'Bearer ' + token }});
			const json = await res.json();
			stats.textContent = JSON.stringify(json, null, 2);
			const v = json.verifications || {success:0,failure:0};
			drawChart(v.success||0, v.failure||0);
		};
		</script>
	</body>
	</html>
	"""


