from typing import Any
from puepy import Application, Page, t
from puepy.runtime import setTimeout, create_proxy
from pyscript import fetch
from json import dumps

app = Application()


async def post(url: str, json: dict[str, Any]) -> dict[str, Any]:
    response = await fetch(url, method="POST", body=dumps(json), headers={"Content-Type":"application/json"})
    body = await response.json()
    print(body)
    return body

@app.page()
class HelloWorldPage(Page):

    def initial(self):
        return {
            "stage": "",
            "problem": "",
            "task_plan":[],
            "expected_output": "",
            "code": "",
            "next_stage":"",
            "complete": False,
            "iteration_count": 0,
            "output": None
        }

    def populate(self):
       with t.div(classes="container"):
           with t.div(classes="row"):
                with t.div(classes="col-6"):
                    t.label(
                        "Problem",
                        t.textarea(classes="form-control", bind="problem", rows=25, cols=100),
                        classes="form-label",
                    )

                    t.button("Solve", classes="btn btn-primary", on_click=self.solve_button_click)
                    

                with t.div(classes="col-6"):
                    if self.state['stage'] != "":
                        t.h3(f"Stage: {self.state['stage']}")

                    if len(self.state["task_plan"]) > 0 and self.state["code"] == "":
                        # Render the task plan on a card
                        with t.div(classes="card"):
                            with t.div(classes="card-header"):
                                t.p("Task Plan")
                            with t.div(classes="card-body"):
                                with t.ul(classes="list-group"):
                                    for item in self.state["task_plan"]:
                                        t.li(item, classes="list-group-item")

                    if self.state["expected_output"] and self.state["stage"] != "Complete":
                        with t.div(classes="card"):
                            with t.div(classes="card-header"):
                                t.p("Expected Output")
                            with t.div(classes="card-body"):
                                t.p(self.state['expected_output'], classes="card-text")

                    if self.state["expected_output"] != "" and self.state["stage"] == "Complete":
                        with t.div(classes="card"):
                            with t.div(classes="card-header"):
                                t.p("Expected Output")
                            with t.div(classes="card-body"):
                                if self.state["test_result"]["passed"]:
                                    t.p(f"Expected Result: {self.state['expected_output']}", classes="card-text")
                                    t.p(f"Acceptance Reason: {self.state['test_result']['reason']}")
                                else:
                                    t.p(f"Expected Result: {self.state['expected_output']}", classes="card-text")
                                    t.p(f"Error: {self.state['test_result']['error']}")
                    
                    if self.state["code"] != "":
                        with t.div(classes="card"):
                            with t.div(classes="card-header"):
                                with t.div(classes="row"):
                                    with t.div(classes="col-3"):
                                        t.p("Current Solution")
                                    
                                    with t.div(classes="col-6"):
                                        pass

                                    with t.div(classes="col-3"):
                                        t.button("Run Code", classes="btn btn-sm btn-success", on_click=self.on_code_execute_click)
                            with t.div(classes="card-body"):
                                t.textarea(classes="form-control", bind="code", rows=25, cols=100),
    
                            if self.state["output"] is not None:
                                with t.div(classes="card-footer"):
                                    if self.state["output"]["exit_code"] != 0:
                                        t.p(self.state["output"]["stderr"], classes="card-text")
                                    else:
                                        t.p(self.state["output"]["stdout"], classes="card-text")

    def solve_button_click(self, event):
        self.state['stage'] = "Task Planning"

    def on_stage_change(self, event):
        setTimeout(create_proxy(self._do_next_stage), 100)

    async def _do_next_stage(self):
        stage = self.state['stage']

        if stage == "Task Planning":
            self.state["task_plan"] = await post("http://localhost:8000/generate_task_plan", json={"problem": self.state["problem"]})
            self.update_stage("Extracting Output")

        elif stage == "Extracting Output":
            self.state["expected_output"] = (await post("http://localhost:8000/extract_solution", json={"problem":self.state['problem']}))['solution']
            self.update_stage("Generating Code")

        elif stage == "Generating Code":
            self.state['code'] = (await post('http://localhost:8000/generate_code', json={"problem": self.state["problem"], "expected_output":self.state["expected_output"]}))["code"]
            self.update_stage("Testing Code")

        elif stage == "Testing Code" and not self.state['complete']:
            self.state['test_result'] = await post("http://localhost:8000/test_solution", json={
                "problem": self.state["problem"],
                "expected_output": self.state["expected_output"],
                "code": self.state["code"]
            })

            if self.state['test_result']["passed"] or self.state["iterations"] >= 3:
                self.update_stage("Complete")
            else:
                self.update_stage("Debugging")
        elif stage == "Debugging" and not self.state["complete"]:
            self.state["code"] = (await post("http://localhost:8000/debug_solution", json={
                "problem": self.state["problem"],
                "expected_output": self.state["expected_output"],
                "code": self.state["code"],
                "test_results": self.state["test_result"]
            }))["code"]

            self.state["iterations"] += 1

    def update_stage(self, stage: str):
        self.state['next_stage'] = stage
        setTimeout(create_proxy(self._activate_stage), 100)

    def _activate_stage(self):
        self.state['stage'] = self.state['next_stage']
        
    async def on_code_execute_click(self, event):
        self.state["output"] = await post("http://localhost:8000/execute", json={"code":self.state["code"]})

app.mount("#app")