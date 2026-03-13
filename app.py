from flask import Flask,request,jsonify,render_template_string
import sympy as sp
import numpy as np
import plotly
import plotly.graph_objs as go
import json
import base64
import io
from PIL import Image
import pytesseract

app=Flask(__name__)

x=sp.symbols('x')

HTML="""
<!DOCTYPE html>
<html>

<head>

<title>Ultimate Math AI</title>

<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>

<style>

body{
background:#111827;
color:white;
font-family:Arial;
text-align:center;
}

input{
padding:10px;
width:350px;
}

button{
padding:10px;
margin:5px;
}

canvas{
border:2px solid white;
}

#graph{
width:800px;
margin:auto;
}

</style>

</head>

<body>

<h1>Ultimate Math AI Platform</h1>

<input id="expr" placeholder="Enter math expression">

<br><br>

<button onclick="solve()">Solve</button>
<button onclick="simplify()">Simplify</button>
<button onclick="derivative()">Derivative</button>
<button onclick="integral()">Integral</button>
<button onclick="limit()">Limit</button>
<button onclick="explain()">AI Tutor</button>

<br>

<button onclick="graph()">2D Graph</button>
<button onclick="graph3d()">3D Graph</button>

<h2 id="result"></h2>

<div id="graph"></div>

<hr>

<h2>Scientific Calculator</h2>

<input id="calc">

<button onclick="calculate()">Calculate</button>

<hr>

<h2>Draw Equation</h2>

<canvas id="draw" width="400" height="200"></canvas>

<br>

<button onclick="clearCanvas()">Clear</button>

<hr>

<h2>Camera Math Solver</h2>

<button onclick="startCamera()">Start Camera</button>
<button onclick="capture()">Capture</button>

<br><br>

<video id="camera" width="400" autoplay></video>
<canvas id="canvas" width="400" height="300" style="display:none"></canvas>

<script>

async function solve(){

let expr=document.getElementById("expr").value

let r=await fetch("/solve",{method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({expr:expr})})

let data=await r.json()

document.getElementById("result").innerText=data.result

}

async function simplify(){

let expr=document.getElementById("expr").value

let r=await fetch("/simplify",{method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({expr:expr})})

let data=await r.json()

document.getElementById("result").innerText=data.result

}

async function derivative(){

let expr=document.getElementById("expr").value

let r=await fetch("/derivative",{method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({expr:expr})})

let data=await r.json()

document.getElementById("result").innerText=data.result

}

async function integral(){

let expr=document.getElementById("expr").value

let r=await fetch("/integral",{method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({expr:expr})})

let data=await r.json()

document.getElementById("result").innerText=data.result

}

async function limit(){

let expr=document.getElementById("expr").value

let r=await fetch("/limit",{method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({expr:expr})})

let data=await r.json()

document.getElementById("result").innerText=data.result

}

async function explain(){

let expr=document.getElementById("expr").value

let r=await fetch("/explain",{method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({expr:expr})})

let data=await r.json()

document.getElementById("result").innerText=data.result

}

async function graph(){

let expr=document.getElementById("expr").value

let r=await fetch("/graph",{method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({expr:expr})})

let data=await r.json()

Plotly.newPlot("graph",data.graph)

}

async function graph3d(){

let r=await fetch("/graph3d",{method:"POST"})

let data=await r.json()

Plotly.newPlot("graph",data.graph)

}

function calculate(){

let val=document.getElementById("calc").value

try{
document.getElementById("calc").value=eval(val)
}catch{
alert("Invalid")
}

}

let canvas=document.getElementById("draw")
let ctx=canvas.getContext("2d")

let drawing=false

canvas.onmousedown=()=>drawing=true
canvas.onmouseup=()=>drawing=false

canvas.onmousemove=(e)=>{

if(!drawing) return

ctx.lineWidth=3
ctx.lineCap="round"

ctx.lineTo(e.offsetX,e.offsetY)
ctx.stroke()

ctx.beginPath()
ctx.moveTo(e.offsetX,e.offsetY)

}

function clearCanvas(){
ctx.clearRect(0,0,canvas.width,canvas.height)
}

async function startCamera(){

let video=document.getElementById("camera")

let stream=await navigator.mediaDevices.getUserMedia({video:true})

video.srcObject=stream

}

async function capture(){

let video=document.getElementById("camera")
let canvas=document.getElementById("canvas")
let ctx=canvas.getContext("2d")

ctx.drawImage(video,0,0,400,300)

let image=canvas.toDataURL("image/png")

let r=await fetch("/image",{method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({img:image})})

let data=await r.json()

document.getElementById("result").innerText=
"Detected: "+data.text+" | Answer: "+data.result

}

</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/solve",methods=["POST"])
def solve():
    expr=request.json["expr"]
    return jsonify({"result":str(sp.solve(expr))})

@app.route("/simplify",methods=["POST"])
def simplify():
    expr=request.json["expr"]
    return jsonify({"result":str(sp.simplify(expr))})

@app.route("/derivative",methods=["POST"])
def derivative():
    expr=request.json["expr"]
    return jsonify({"result":str(sp.diff(expr,x))})

@app.route("/integral",methods=["POST"])
def integral():
    expr=request.json["expr"]
    return jsonify({"result":str(sp.integrate(expr,x))})

@app.route("/limit",methods=["POST"])
def limit():
    expr=request.json["expr"]
    return jsonify({"result":str(sp.limit(expr,x,0))})

@app.route("/explain",methods=["POST"])
def explain():
    expr=request.json["expr"]
    steps="Step 1: Analyze expression → "+expr+" | Step 2: Apply symbolic rules | Step 3: Compute result."
    return jsonify({"result":steps})

@app.route("/graph",methods=["POST"])
def graph():

    expr=request.json["expr"]

    f=sp.lambdify(x,expr,"numpy")

    X=np.linspace(-10,10,200)
    Y=f(X)

    graph=[go.Scatter(x=X,y=Y)]

    return jsonify({"graph":json.loads(json.dumps(graph,cls=plotly.utils.PlotlyJSONEncoder))})

@app.route("/graph3d",methods=["POST"])
def graph3d():

    X=np.linspace(-5,5,50)
    Y=np.linspace(-5,5,50)

    X,Y=np.meshgrid(X,Y)

    Z=np.sin(np.sqrt(X**2+Y**2))

    graph=[go.Surface(x=X,y=Y,z=Z)]

    return jsonify({"graph":json.loads(json.dumps(graph,cls=plotly.utils.PlotlyJSONEncoder))})

@app.route("/image",methods=["POST"])
def image():

    data=request.json["img"]

    img_bytes=base64.b64decode(data.split(",")[1])

    img=Image.open(io.BytesIO(img_bytes))

    text=pytesseract.image_to_string(img)

    try:
        expr=sp.sympify(text)
        result=sp.solve(expr)
    except:
        result="Could not solve"

    return jsonify({"text":text,"result":str(result)})

app.run(debug=True)
