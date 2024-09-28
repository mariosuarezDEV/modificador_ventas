import { NextResponse } from "next/server";

export const GET = () =>{
    return NextResponse.json({message: "Informacion de la empresa"});
}

export const PUT = () =>{
    return NextResponse.json({message: "Actualizando la empresa"});
}

export const DELETE = () =>{
    return NextResponse.json({message: "Eliminando la empresa"});
}