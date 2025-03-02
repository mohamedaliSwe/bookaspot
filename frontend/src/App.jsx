import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import Nav from './components/Nav';
import Landing from './components/Landing';
import AmenityDetails from './components/AmenityDetails';
import Booking from './components/Booking';
import Profile from './components/Profile';
import Amenities from './components/Amenities';
import Login from './components/Login';
import Signup from './components/Signup';
import { Footer } from './components/Footer';

const App = () => {
  return (
    <Router>
      <Nav />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/amenities" element={ <Amenities /> } />
        <Route path="/amenities/:id" element={<AmenityDetails />} />
        <Route path="/bookings/new" element={<Booking />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={ <Signup />} />
      </Routes>
      <Footer/>
    </Router>
  );
};

export default App;
