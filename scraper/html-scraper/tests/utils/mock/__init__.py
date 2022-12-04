import pathlib

import jinja2
import jinja2.sandbox

env = jinja2.sandbox.SandboxedEnvironment(
    loader=jinja2.FileSystemLoader(
        pathlib.PurePath(__file__).parent / "template"),
    autoescape=jinja2.select_autoescape,
)
template = env.get_template("index.jinja")

if __name__ == "__main__":
    print(
        template.render(title="king of the north",
                        links=[dict(href="aaa", caption="bbb")]))
