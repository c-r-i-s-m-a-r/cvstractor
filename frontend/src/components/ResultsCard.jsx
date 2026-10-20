import Highlight from './Highlight.jsx'
import { textoDe } from '../search.js'

const ETIQUETAS = {
  institution: 'Institución',
  degree: 'Título',
  graduation_year: 'Año de graduación',
  company: 'Empresa',
  position: 'Puesto',
  start_date: 'Fecha de inicio',
  end_date: 'Fecha de fin',
  description: 'Descripción',
}

function Campo({ etiqueta, valor, consulta }) {
  const texto =
    typeof valor === 'string' || typeof valor === 'number'
      ? String(valor).trim()
      : ''
  return (
    <div className="campo">
      <span className="campo-etiqueta">{etiqueta}</span>
      <span className={texto ? 'campo-valor' : 'campo-valor vacio'}>
        {texto ? <Highlight texto={texto} consulta={consulta} /> : 'No encontrado'}
      </span>
    </div>
  )
}

function Seccion({ titulo, children }) {
  return (
    <section className="seccion">
      <h3>{titulo}</h3>
      {children}
    </section>
  )
}

function entradaDatos(item, consulta) {
  if (item == null || item === '') return null
  if (typeof item !== 'object') {
    return (
      <p className="entrada-texto">
        <Highlight texto={String(item)} consulta={consulta} />
      </p>
    )
  }
  const campos = Object.entries(item).filter(
    ([, v]) => v != null && String(v).trim() !== ''
  )
  if (campos.length === 0) return null
  return (
    <div className="ficha">
      {campos.map(([clave, valor]) => (
        <Campo
          key={clave}
          etiqueta={ETIQUETAS[clave] || clave}
          valor={valor}
          consulta={consulta}
        />
      ))}
    </div>
  )
}

function listaDe(valor) {
  if (Array.isArray(valor)) return valor
  if (valor == null || valor === '') return []
  return [valor]
}

export default function ResultsCard({ datos, consulta, nombreArchivo }) {
  const personal = datos.personal || {}
  const contacto = datos.contacto || {}
  const educacion = listaDe(datos.educacion)
  const experiencia = listaDe(datos.experiencia)
  const habilidades = listaDe(datos.habilidades)
  const resumen = typeof datos.resumen === 'string' ? datos.resumen.trim() : ''
  const sinDatos = textoDe(datos).trim() === ''

  return (
    <article className="resultado">
      <header className="resultado-cabecera">
        <h2>Resultado</h2>
        <span className="resultado-archivo">{nombreArchivo}</span>
      </header>

      {sinDatos && (
        <p className="aviso" role="alert">
          El documento no contenía datos reconocibles.
        </p>
      )}

      <div className="resultado-cuerpo">
        <Seccion titulo="Datos personales">
          <Campo etiqueta="Nombre" valor={personal.nombre} consulta={consulta} />
          <Campo etiqueta="Email" valor={personal.email} consulta={consulta} />
          <Campo etiqueta="Teléfono" valor={personal.telefono} consulta={consulta} />
          <Campo etiqueta="Dirección" valor={personal.direccion} consulta={consulta} />
        </Seccion>

        <Seccion titulo="Contacto">
          <Campo etiqueta="GitHub" valor={contacto.github} consulta={consulta} />
          <Campo etiqueta="LinkedIn" valor={contacto.linkedin} consulta={consulta} />
          <Campo etiqueta="Web" valor={contacto.web} consulta={consulta} />
        </Seccion>

        <Seccion titulo="Educación">
          {educacion.length === 0 ? (
            <p className="campo-valor vacio">No encontrado</p>
          ) : (
            educacion.map((item, i) => (
              <div key={i}>{entradaDatos(item, consulta)}</div>
            ))
          )}
        </Seccion>

        <Seccion titulo="Experiencia">
          {experiencia.length === 0 ? (
            <p className="campo-valor vacio">No encontrado</p>
          ) : (
            experiencia.map((item, i) => (
              <div key={i}>{entradaDatos(item, consulta)}</div>
            ))
          )}
        </Seccion>

        <Seccion titulo="Habilidades">
          {habilidades.length === 0 ? (
            <p className="campo-valor vacio">No encontrado</p>
          ) : (
            <ul className="chips">
              {habilidades.map((item, i) => (
                <li key={i} className="chip">
                  <Highlight texto={String(item)} consulta={consulta} />
                </li>
              ))}
            </ul>
          )}
        </Seccion>

        <Seccion titulo="Resumen">
          {resumen ? (
            <p className="entrada-texto">
              <Highlight texto={resumen} consulta={consulta} />
            </p>
          ) : (
            <p className="campo-valor vacio">No encontrado</p>
          )}
        </Seccion>
      </div>
    </article>
  )
}
