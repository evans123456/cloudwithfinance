from flask import Flask, render_template, request,redirect,url_for, jsonify


app = Flask(__name__)


@app.route('/',methods = ["POST","GET"])
def home():
    if request.method == "POST":
        service = request.form["service"]
        resource = request.form["resources"]

        print(service,resource)

        if service == "ec2":
            warm_up_resources(resource)
            return redirect(url_for("resources",srv=service,r=resource))
        else: #if lambda
            return redirect(url_for("resources",srv=service,r=resource))
        


    else:
        return render_template("home.html")


def warm_up_resources(num_resources):
    print("Warming up resources...")

    print("creating ec2 instances...")

    print("EC2 instances created successfully!")




@app.route("/<srv>/<r>",methods = ["POST","GET"])
def resources(srv,r):
    if request.method == "POST":
        # no_of_resources = request.form["no_of_resource"]    
        
        
        print("Finished creating instances")
        return redirect(url_for("lastPage",srvce=srv,R=no_of_resources))

        
    else:
        return render_template("risk_analysis.html",content=srv)























































@app.route("/audit",methods = ["GET"])
def audit():
    items = []
    # docs = db.collection("history").get()
    # for doc in docs:
    #     items.append(doc.to_dict())

    # items = reversed(items)
    return render_template("audit.html",vals=items)







# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''