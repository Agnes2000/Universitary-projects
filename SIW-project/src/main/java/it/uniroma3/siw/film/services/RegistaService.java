package it.uniroma3.siw.film.services;

import static java.util.stream.Collectors.toList;
import static java.util.stream.StreamSupport.stream;

import javax.transaction.Transactional;

import java.util.List;
import org.springframework.stereotype.Service;

import it.uniroma3.siw.film.model.Regista;
import it.uniroma3.siw.film.repository.RegistaRepository;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class RegistaService {
    
    private final RegistaRepository registaRepository;

    @Transactional
    public Regista salvaRegista(Regista regista){
        return this.registaRepository.save(regista);
    }

    public List<Regista> getRegisti(){
        return stream(this.registaRepository.findAll().spliterator(), false).collect(toList());
    }

    @Transactional
    public Regista getRegista(Long id){
        return this.registaRepository.findById(id).get();
    }

    @Transactional
    public void cancellaRegista(Long id){
        this.registaRepository.deleteById(id);
    }
}
