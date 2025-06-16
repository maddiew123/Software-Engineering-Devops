import './styling/App.css'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Login from './pages/Login'
import Profile from './pages/Profile'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import CreateNewMatch from './pages/CreateNewMatch'

import ViewAllTeams from './pages/ViewAllTeams'
import SignUp from './pages/SignUp'

const queryClient = new QueryClient();

function App() {

  return (

    <>
   
      <QueryClientProvider client={queryClient}>
      <BrowserRouter>
       
    <Routes>
      <Route path="/" element = {<Login/>}/>
      <Route path="/profile" element = {<Profile/>}/>
      <Route path="/match/create" element = {<CreateNewMatch/>}/>

      <Route path="/teams" element = {<ViewAllTeams/>}/>
      <Route path="/signup" element = {<SignUp/>}/>
    </Routes>
    </BrowserRouter>
    </QueryClientProvider>
    </>
  )
}

export default App
