import asyncio
import json

from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing.queues import Empty

from pingtest import Ping
from pingtest import PingReport


class Worker(Process):
    def __init__(self, iq: Queue, oq: Queue):
        super().__init__()
        self.iq = iq
        self.oq = oq

    def run(self):
        while True:
            try:
                link = self.iq.get(timeout=3)
            except Empty:
                break
            ping = Ping(link)
            result = ping.run()

            self.oq.put(result)

            url = result["addr"]
            loss = result["loss"]
            mint = result["mint"]
            maxt = result["maxt"]
            avgt = result["avgt"]
            print(f"{url:30} {loss:5} {mint:5} {maxt:5} {avgt:5}")


def main():
    with open("resources/vultr-ip.txt", "rt", encoding="utf-8") as res:
        links = res.read().strip().split("\n")

    linksq = Queue()
    resultsq = Queue()
    results = []
    for i in links:
        linksq.put(i)

    ws = [Worker(linksq, resultsq) for _ in range(4)]

    for i in ws:
        i.start()

    for i in ws:
        i.join()

    while True:
        try:
            res = resultsq.get(timeout=3)
            results.append(res)
        except Empty:
            break

    return results


if __name__ == "__main__":
    print(f"{'addr':30} {'loss':5} {'mint':5} {'maxt':5} {'avgt':5}")
    print()
    results = main()
    obj = {
        "name": "vultr ping",
        "data": results
    }
    with open("vultr-result.json", "wt", encoding="utf-8") as t:
        json.dump(obj, t, ensure_ascii=False, indent=1)
