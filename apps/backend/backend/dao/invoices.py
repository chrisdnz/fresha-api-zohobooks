from database.prisma.connection import prisma

async def get_all_invoices():
    return await prisma.invoice.find_many()