package it.uniroma3.siw.film.repository;

import java.util.Optional;

import org.springframework.data.repository.CrudRepository;


import it.uniroma3.siw.film.model.Credenziali;


public interface CredenzialiRepository extends CrudRepository<Credenziali, Long> {

    public Optional<Credenziali> findByUsername(String username);
	public boolean existsByUsername(String username);
    
}
