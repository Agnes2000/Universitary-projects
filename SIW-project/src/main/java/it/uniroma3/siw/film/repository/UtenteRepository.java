package it.uniroma3.siw.film.repository;

import org.springframework.data.repository.CrudRepository;


import it.uniroma3.siw.film.model.Utente;


public interface UtenteRepository extends CrudRepository<Utente, Long> {
    
}
