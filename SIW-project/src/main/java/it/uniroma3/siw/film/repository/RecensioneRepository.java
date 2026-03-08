package it.uniroma3.siw.film.repository;

import java.util.List;

import org.springframework.data.repository.CrudRepository;


import it.uniroma3.siw.film.model.Film;
import it.uniroma3.siw.film.model.Recensione;
import it.uniroma3.siw.film.model.Utente;

public interface RecensioneRepository  extends CrudRepository<Recensione, Long>{
    
     public List<Recensione> findByUtente(Utente utente);

     public boolean existsByUtenteAndFilm(Utente utente, Film film);

}
