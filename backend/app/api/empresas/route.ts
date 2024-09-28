import { NextResponse } from "next/server";
import { prisma } from '@/libs/conect_prisma'

export const GET = async () => {
    try {
        const ver_empresas = await prisma.empresa.findMany()
        return NextResponse.json({
            notificacion: "Empresas encontradas",
            empresas: ver_empresas
        }, {
            status: 200
        })
    } catch (err) {
        return NextResponse.json({
            notificacion: "Error al obtener las empresas",
            error: err
        }, {
            status: 400
        })
    }

}

export const POST = async (request : Request) => {
    const {nombre, direccion} = await request.json()

    try {
        const nueva_empresa = await prisma.empresa.create({
            data:{
                nombre,
                direccion
            }
        })

        return NextResponse.json({
            notificacion: "La empresa se creo con éxito",
            datos: nueva_empresa
        }, {
            status: 201
        });
    } catch (err) {
        return NextResponse.json({
            notificacion: "Error al crear la empresa",
            error: err
        }, {
            status: 400
        });
    }

}