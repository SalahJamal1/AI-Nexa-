# This is a sample Python script.
import asyncio

from graph.graph import app


# Press ⌃F5 to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press F9 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    res = asyncio.run(app.ainvoke({"file_path": "Salah_AbuFarha_Developer.pdf", "job_role": "AI engineer"}))
    print(res)
    app.get_graph().draw_mermaid_png(output_file_path="graph.png")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
