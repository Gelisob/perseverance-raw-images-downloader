import asyncio
import json
from asyncio import BoundedSemaphore
from datetime import datetime, timedelta
from glob import glob
from pathlib import Path
from sys import stderr

import httpx
from httpx import AsyncClient

url = "https://mars.nasa.gov/rss/api/"
params = {
    "feed": "raw_images",
    "category": "mars2020,ingenuity",
    "feedtype": "json",
    "order": "sol desc",
    "ver": "1.2",
}
page_size = 100
max_parallel = 16
max_db_age = timedelta(days=1)


async def getDb(start: int, client: AsyncClient, sem: BoundedSemaphore):
    async with sem:
        print(f"starting getDb #{start}", file=stderr)
        res = (
            await client.get(
                url, params={**params, "num": page_size, "page": start // page_size}
            )
        ).json()["images"]
        print(f"finished getDb #{start} {len(res)}", file=stderr)
        return res


async def getImage(
    result: dict, client: AsyncClient, sem: BoundedSemaphore, index: int, total: int
):
    async with sem:
        print(f"starting getImage {index:6} /{total:6}", file=stderr)

        url = result["image_files"]["full_res"]

        filename = Path(url).name
        dirpath = Path(
            Path("images") / result["camera"]["instrument"] / result["sample_type"]
        )
        filepath = Path(dirpath / filename)
        if filepath.exists():
            print(f"Nothing to do for {index:6} /{total:6}", file=stderr)
        else:
            img = (await client.get(url)).content
            dirpath.mkdir(parents=True, exist_ok=True)
            with open(dirpath / filename, "wb") as f:
                f.write(img)
            print(
                f"finished getImage {index:6} /{total:6} => {len(img):10}", file=stderr
            )


def write_db(db):
    with open(f"db_{datetime.now().isoformat()}.json", "w") as f:
        json.dump(db, f)


def read_db():
    cur_date = datetime.now()
    for filename in sorted(glob("db_*.json"), reverse=True):
        try:
            file_date = datetime.fromisoformat(filename[3:-5])
            if cur_date - file_date <= max_db_age:
                with open(filename) as f:
                    return json.load(f)
            else:
                print(f"{file_date} too old")
        except:
            pass
    return None


async def main():
    async with AsyncClient(timeout=10) as client:
        if (db := read_db()) is None:
            r = await client.get(url, params={**params, "num": 0})
            info = r.json()
            total = info["total_results"]
            sem = BoundedSemaphore(max_parallel)
            db = [
                img
                for lst in await asyncio.gather(
                    *(getDb(start, client, sem) for start in range(0, total, page_size))
                )
                for img in lst
            ]
            write_db(db)

        sem = BoundedSemaphore(max_parallel)
        await asyncio.gather(
            *(getImage(res, client, sem, i, len(db)) for i, res in enumerate(db))
        )


asyncio.run(main())
