from backend.database.prisma.connection import prisma

async def create_customer(name: str):
    return await prisma.customer.create(
        data={
            'name': name
        }
    )