/**
 * Crea en Google Forms el consentimiento informado del estudio
 * "Efecto del estado emocional sobre el desempeño en la búsqueda visual"
 * (Proyectos Integradores V-1, Fundación Universitaria Konrad Lorenz).
 *
 * Cómo usarlo:
 * 1. Entra a https://script.google.com con tu cuenta de Google y pulsa "Nuevo proyecto".
 * 2. Borra el código que aparece, pega todo este archivo y guarda (Ctrl + S).
 * 3. Arriba, elige la función "crearFormulario" y pulsa "Ejecutar".
 *    La primera vez Google pide permisos: "Revisar permisos" > tu cuenta > "Permitir".
 * 4. Abre el "Registro de ejecución": ahí salen el enlace para editar el formulario
 *    y el enlace para enviarlo a los participantes. El formulario queda en tu Google Drive.
 *
 * Cada vez que ejecutes la función se crea un formulario nuevo.
 */

const TITULO = 'Consentimiento informado';

const INTRODUCCION =
  'Usted ha sido invitado(a) a participar en el estudio titulado «Efecto del estado emocional ' +
  'sobre el desempeño en la búsqueda visual». Esta investigación es conducida por Alzate, J., ' +
  'Ballen, V., Bohórquez, M., Moreno, M. y Ortiz, D., del programa de Psicología de la ' +
  'Fundación Universitaria Konrad Lorenz.\n\n' +
  'Lea cada sección y marque la casilla para confirmar que la comprende. ' +
  'Al final encontrará el espacio para dar su consentimiento, su número de cédula y la fecha.\n\n' +
  '(Modelo utilizado para el trabajo de Proyectos Integradores V-1)';

const SECCIONES = [
  {
    titulo: 'Propósito del estudio',
    texto:
      'El propósito de este estudio es determinar el efecto del estado emocional sobre el ' +
      'desempeño en la búsqueda visual. Entiendo que la información que pueda ser recolectada ' +
      'por mi participación en el estudio será usada para temas exclusivamente académicos.',
  },
  {
    titulo: 'Descripción del procedimiento',
    texto:
      'Es un estudio de tipo experimental con un diseño cuasiexperimental y unifactorial. ' +
      'El procedimiento comprende las siguientes fases: 1) invitación y clasificación de los ' +
      'participantes en los grupos experimentales y control; 2) presentación de los cortos ' +
      'cinematográficos; 3) aplicación de la prueba; 4) análisis de resultados. El participante ' +
      'acepta y diligencia el consentimiento informado para poder ser clasificado en alguna de ' +
      'las condiciones experimentales, para la posterior lectura del escenario hipotético y la ' +
      'aplicación de la prueba.',
  },
  {
    titulo: 'Retribución y beneficios por la participación',
    texto:
      'Por la participación en este estudio no existe ningún tipo de incentivo, por tratarse ' +
      'de una investigación netamente académica.',
  },
  {
    titulo: 'Riesgos e incomodidades',
    texto:
      'Tenga en cuenta que en este estudio no se aplican procedimientos que supongan daño o ' +
      'riesgo para usted o para otros.',
  },
  {
    titulo: 'Confidencialidad',
    texto:
      'Entiendo que cualquier información personal que haga parte de los resultados de la ' +
      'investigación será mantenida de manera confidencial. En ninguna publicación en la que ' +
      'se usen mis resultados se mencionará mi nombre a menos que lo consienta y autorice ' +
      'por escrito.',
  },
  {
    titulo: 'Participación voluntaria',
    texto:
      'La participación en este estudio es voluntaria. Entiendo que tengo la libertad de ' +
      'retirar mi consentimiento de participación en esta investigación en cualquier momento ' +
      'y que en tal caso no tendré ningún tipo de repercusión.',
  },
  {
    titulo: 'Información',
    texto:
      'Para obtener información acerca de esta investigación puedo comunicarme con ' +
      'mariaf.morenog1@konradlorenz.edu.co. También puedo pedir a ese correo una copia de ' +
      'este consentimiento para mi archivo personal.',
  },
];

function crearFormulario() {
  const form = FormApp.create(TITULO);
  form
    .setDescription(INTRODUCCION)
    .setProgressBar(true)
    .setAllowResponseEdits(false)
    .setConfirmationMessage('Gracias. Su consentimiento quedó registrado.');

  // Página 1: cada sección del documento, con una casilla obligatoria de "leí y comprendo".
  SECCIONES.forEach(function (seccion) {
    form
      .addCheckboxItem()
      .setTitle(seccion.titulo)
      .setHelpText(seccion.texto)
      .setChoiceValues(['He leído y comprendo esta información'])
      .setRequired(true);
  });

  // Página 2: consentimiento y datos del participante (lo que en papel era la firma).
  form
    .addPageBreakItem()
    .setTitle('Consentimiento y datos del participante');

  form
    .addMultipleChoiceItem()
    .setTitle('¿Consiente voluntariamente participar en este estudio?')
    .setChoiceValues([
      'Sí, consiento voluntariamente participar en este estudio',
      'No deseo participar',
    ])
    .setRequired(true);

  form
    .addTextItem()
    .setTitle('Nombre completo del participante')
    .setRequired(true);

  const soloNumeros = FormApp.createTextValidation()
    .setHelpText('Escriba solo números, sin puntos ni espacios.')
    .requireTextMatchesPattern('^[0-9]{5,12}$')
    .build();
  form
    .addTextItem()
    .setTitle('Número de cédula')
    .setHelpText('Sin puntos ni espacios. Ejemplo: 1012345678')
    .setValidation(soloNumeros)
    .setRequired(true);

  form
    .addDateItem()
    .setTitle('Fecha')
    .setHelpText('Día, mes y año en que firma este consentimiento.')
    .setIncludesYear(true)
    .setRequired(true);

  // Los formularios creados por código pueden quedar sin publicar; si el método existe, se publica.
  try {
    form.setPublished(true);
  } catch (e) {
    // Versiones de Apps Script sin setPublished: el formulario ya acepta respuestas.
  }

  Logger.log('Enlace para editar: ' + form.getEditUrl());
  Logger.log('Enlace para los participantes: ' + form.getPublishedUrl());
}
