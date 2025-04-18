# from rantevou.src.controller.logging import Logger
# from rantevou import __main__

# __main__.main()
from time import perf_counter
from rantevou.src.controller.customers_controller import CustomerControl, Customer
from sqlalchemy import or_

import pandas as pd

cc = CustomerControl()
df = pd.read_sql("SELECT * FROM customer", cc.model.session.bind)

customers = cc.get_customers()
queries = [
    "abcdegjmy4@ex",
    "abcdegjmy4@exa",
    "abcdegjmy4@exam",
    "abcdegjmy4@examp",
    "abcdegjmy4@exampl",
    "abcdegjmy4@example",
    "abcdegjmy4@example.c",
    "abcdegjmy4@example.co",
    "abcdegjmy4@example.com",
]
start = perf_counter()

for query in queries:

    df.apply(lambda x: print(x), axis=1)

    # r = (
    #     cc.model.session.query(Customer)
    #     .filter(
    #         or_(
    #             Customer.name.like(f"%{query}%"),
    #             Customer.surname.like(f"%{query}%"),
    #             Customer.email.like(f"%{query}%"),
    #             Customer.phone.like(f"%{query}%"),
    #         )
    #     )
    #     .all()
    # )
    # print(r)

    # for customer in customers:
    #     if (
    #         customer.name.startswith(query)
    #         or customer.surname.startswith(query)
    #         or customer.email.startswith(query)
    #         or customer.phone.startswith(query)
    #     ):
    #         print(customer)
    #         break

print(perf_counter() - start)
