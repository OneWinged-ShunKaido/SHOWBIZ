from asyncio import run, gather, get_event_loop
from typing import List, Union

from aiofiles.ospath import isfile

from production import Production as Prod

from aiohttp import ClientSession, TCPConnector


class ShowBiz(Prod):
    main_session: ClientSession
    second_session: ClientSession
    switch_session: bool = False
    api: str = "https://api.show-biz.net/"
    base_project: str = "api/user/projects/{}/"
    base_material: str = "api/user/materials/{}/"
    current_url: str
    verify: bool = False
    cert_path = ".[insert SSL cert path here]"  # set ^ True (optional for debugging => e.g. using requests + proxy)
    bearer: str = "[insert bearer token here]"

    def __init__(self):
        super().__init__()
        self.session = ClientSession()
        if self.verify:
            #   requests session !!
            self.session.verify = self.cert_path

    async def prepare_request(self, url: str):
        headers = {
            "authorize": f"Bearer {self.bearer}",
            "authorization": f"Bearer {self.bearer}"
        }
        self.current_url = self.api + url
        return headers

    async def send_request(self, url: str, params: dict = '', method: str = 'post',
                           session: ClientSession = None) -> dict:
        headers = await self.prepare_request(url)
        if session:
            async with session.request(url=self.current_url, method=method, headers=headers, params=params) as r:
                if r.status == 200:
                    return dict(await r.json())

        async with self.session as session:
            async with session.request(url=self.current_url, method=method, headers=headers, params=params) as r:
                if r.status == 200:
                    return dict(await r.json())

    async def sign_in(self):
        #   TODO: Add Google + Email login
        ...

    async def get_product_by_page(self, page_no: int = 1, prod_per_page: int = 10000) -> Union[List[dict], bool]:
        url = (self.base_project.format(self.project_id) +
               f"material?sort_type=new&page={page_no}&per_page={prod_per_page}")
        products = await self.send_request(url)
        if not products:
            return False

        return products.get("data")

    async def get_single_production(self, production_id: int, session):
        #   prod_id = prod.get("material_id")
        res = await self.send_request(self.base_material.format(production_id), method='get', session=session)
        return res

    async def get_products(self, page_no: int = 1, prod_per_page: int = 10000, save_prods: bool = False):
        products = await self.get_product_by_page(page_no, prod_per_page)
        self.products = products
        print(f"\nFound {len(products)} productions !")

        if not save_prods:
            return

        tasks = []
        connector = TCPConnector(limit=10000)
        i = 1
        async with ClientSession(connector=connector) as session:
            self.session = session
            for production in products:
                task = self.get_single_production(production.get("id"), session)
                i += 1
                tasks.append(task)

            results = await gather(*tasks)

        if save_prods:
            for res in results:
                self.productions.append(res)
            await self.save_prods()

    """
    async def get_products(self, page_no: int = 1, prod_per_page: int = 10000, save_prods: bool = False):
        products = await self.get_product_by_page(page_no, prod_per_page)
        print(f"\nFound {len(products)} productions !")
        if save_prods:
            connector = TCPConnector(limit=10000)
            async with ClientSession(connector=connector) as session:
                self.session = session
                for production in products:
                    res = await self.get_single_production(production.get("id"), session)
                    self.productions.append(res)
                await self.save_prods()
    """

    async def download_preview(self):
        preview = self.material_detail.get("preview_list", [])
        for element in preview:
            self.preview = element
            fp = self.prod_path + "/{}".format(self.format_name(self.preview.get("file_name")))
            if not await isfile(fp):
                try:
                    async with self.session.get(element.get("url")) as response:
                        if response.status == 200:
                            await self.save_preview(fp, await response.read())
                except Exception as e:
                    print(f"An error occurred while downloading {fp}: {e}")
                    self.session = ClientSession(connector=TCPConnector(limit=10000))
                    try:
                        async with self.session.get(element.get("url")) as response:
                            if response.status == 200:
                                await self.save_preview(fp, await response.read())
                    except Exception as e:
                        print(f"Failed to download {element.get('url')}: {e}")

    async def save_prods(self):
        for production in self.productions:
            self.production = production.get("data")
            await self.load_prod()
            await self.download_works()

    async def download_works(self):
        await self.save_production()
        await self.download_preview()
        await self.download_parts()

    async def load_production(self):
        ...

    async def verify_dl(self):
        authors = []
        for product in self.products:
            an = self.format_name(product.get("user_profile", {}).get("username_international")) + "_" + str(
                product.get("user_profile", {}).get("id"))
            authors.append(an)

        authors = list(set(authors))
        print(authors)
        print(len(authors))
