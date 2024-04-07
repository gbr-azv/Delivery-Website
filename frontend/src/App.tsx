interface BotaoProps{
  msg: string
}

function Botao(props: BotaoProps){
  console.log(props);
  return <button className="button">{props.msg}</button>
}

export function App() {
  return (
    <div>
      <Botao msg="Click Here"/>
    </div>
  )
}