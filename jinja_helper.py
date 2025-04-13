import jinja2
import os

def render_path(path, install_location, game_directory,):

    # sanity check input path #
    if not path.endswith(".reg.j2"):
        raise NotImplementedError("Path must end in .reg.j2 for Jinja-Module")

    # build result path #
    result_path = path[:-len(".j2")]

    # prepare template #
    print("JINJA-> cwd: ", os.getcwd(), "path:", path)
    input_content = ""
    with open(path, encoding="utf-16") as f:
        input_content = f.read()

    template = jinja2.Template(input_content)
    print("in", input_content)

    # render #
    output_content = template.render(
        install_dir=install_location.replace("\\", "\\\\"),
        user_home=os.path.expanduser("~").replace("\\", "\\\\")
    )

    # save new file #
    with open(result_path, "w", encoding="utf-16") as f:
        f.write(output_content)

    print(output_content)
    return result_path