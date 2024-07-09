from backend.database.prisma.connection import prisma


async def get_customer_by_id(customer_id: int):
    return await prisma.customer.find_unique(where={'id': customer_id})


async def update_customer(customer_id: int, data: dict):
    return await prisma.customer.update(
        where={'id': customer_id},
        data=data
    )


async def create_customer(name: str):
    return await prisma.customer.create(
        data={
            'name': name
        }
    )