from typing import List
from os import makedirs
from json import dumps

from aiofiles import open as async_open


class Production:
    project_id: int = 0
    as_json: bool = False
    products: List[dict]
    productions: List[dict] = []
    production: dict
    loaded_productions: list
    production_path: str = "./productions/{}/"
    prod_path: str
    material_detail: dict
    source_material_relation: dict
    used_material_list: list
    mix_list: list
    used_work_list: list
    #
    production_id: int
    production_title: str
    production_thumbnail_url: str
    #
    author: str
    user_profile: dict
    user_id: int  # useful if dupes of username exists (maybe?)
    user_icon_url: str
    user_name: str
    user_kana: str
    user_in: str  # username_international
    #
    preview: dict

    creation_date: str

    def __init__(self):
        super().__init__()

    async def load_prod(self):
        production = self.production
        self.material_detail = production.get("material_detail")
        self.source_material_relation = production.get("source_material_relation")
        self.used_material_list = production.get("used_material_list")
        self.mix_list = production.get("mix_list")
        self.used_work_list = production.get("used_work_list")
        """
        print(production, end="\n\n")
        print(self.material_detail.keys(), self.source_material_relation.keys())
        """
        self.set_production_details()

    def set_user_details(self):
        self.user_id = self.user_profile.get("id")
        self.user_icon_url = self.user_profile.get("icon")
        self.user_name = self.user_profile.get("name")
        self.user_kana = self.user_profile.get("id")
        self.user_in = self.user_profile.get("username_international")

    def set_production_details(self):
        self.production_id = self.material_detail.get("id")
        self.production_title = self.material_detail.get("title")
        self.production_thumbnail_url = self.material_detail.get("thumbnail")
        self.user_profile = self.material_detail.get("user_profile")
        self.set_user_details()
        #
        self.author = self.format_name(self.user_in)
        self.prod_path = self.production_path.format(self.project_id) + f"{self.author}_{self.user_id}"

    def create_author_folder(self):
        #   inaccurate func name
        makedirs(self.prod_path, exist_ok=True)

    def create_prod_folder(self):
        self.prod_path += f"/{self.production_id}"
        self.create_author_folder()

    def create_parts_folder(self):
        self.prod_path += f"/parts"
        makedirs(self.prod_path + "/lyrics", exist_ok=True)
        makedirs(self.prod_path + "/audio", exist_ok=True)
        makedirs(self.prod_path + "/video", exist_ok=True)
        makedirs(self.prod_path + "/art", exist_ok=True)
        makedirs(self.prod_path + "/unknown", exist_ok=True)

    async def download_parts(self):
        self.create_parts_folder()

    async def save_prod(self):
        if self.as_json:
            fp = self.prod_path + "/details.json"
            open(fp, "w", encoding='utf-8').write(dumps(self.production, indent=4, ensure_ascii=False))

    async def save_parts(self):
        ...

    async def save_production(self):
        self.create_author_folder()
        self.create_prod_folder()
        await self.save_prod()

    def save_productions(self):
        print("\n\n\n")
        download_list = self.material_detail.get("download_list", [])
        print(download_list)

    def save_production_json(self):
        open(self.prod_path + f"_{self.production_id}.json", 'w', encoding="utf-8").write(dumps(
            dict(details=self.production), indent=4, ensure_ascii=False))

    @staticmethod
    async def save_preview(fp: str, content: bytes):
        async with async_open(fp, "wb") as f:
            await f.write(content)

    """
    @staticmethod
    def save_preview(fp: str, content: bytes):
        open(fp, "wb").write(content)
    """

    @staticmethod
    def format_name(content: str):
        content = content.replace(" ", "_", ).replace("/", "_").replace("\\", "_")
        return content



