# imports
from pydriller import Repository



# class responsible for retreiving data from git repository
class GetRepositoryData:

    def getRepInfo(self, filename, path):
        print(filename, path)
        with open(filename, 'w', newline='', encoding="utf-8") as f:
            f.write(f"filename;developer;commitdate;path;"
                    f"changetype;oldpath;projectname;realpath\n")
            for commit in Repository(path).traverse_commits():
                project_name = commit.project_name
                # for all modifications happened in one commit do
                for m in commit.modified_files:
                    if m.new_path is not None:
                        path = m.new_path.replace('\\', '/')
                    else:
                        path = m.new_path

                    f.write(f"{m.filename};{commit.author.name};"
                            f"{commit.author_date};{m.new_path};"
                            f"{m.change_type};{m.old_path};{project_name};{path}\n")
