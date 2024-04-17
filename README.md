# SHOWBIZ
Use python &amp; SHOWBIZ (https://show-biz.net) api to download resources from showbiz project.

Useful in case nb or participants, creations or inspiration is needed (or any type of additional data)

Usage Example:

```python
from showbiz import ShowBiz


async def main():
    showbiz = ShowBiz()
    showbiz.project_id = 41  # set project id (Ado => 41 & default is 0)
    showbiz.as_json = False  # set save productions as json to false (default is false)
    try:
        await showbiz.sign_in()  #  TODO: email + google login (use bearer token in the meantime)
        await showbiz.get_products(save_prods=True)  # save only preview productions
        await showbiz.verify_dl()

    except Exception as e:
        print(f"Failed to download resources -> {e}")

if __name__ == "__main__":
    get_event_loop().run_until_complete(main())
```


TODO: 
-> Add Google + Email login
-> Fix async/aiohttp download drops
-> Add filter for file type
-> Add filter for file origin
