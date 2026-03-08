package it.uniroma3.siw.film.controllers.components.validators;

import org.springframework.stereotype.Component;
import org.springframework.validation.Errors;
import org.springframework.validation.Validator;

import it.uniroma3.siw.film.model.Regista;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Component
@RequiredArgsConstructor
public class RegistaValidator implements Validator {
    
    @Override
    public void validate(Object target, Errors errors) {
        log.info("Validazione Regista Iniziata");
        log.info("Validazione Regista Terminata");
    }
    
    @Override
    public boolean supports(Class<?> clazz) {
        return Regista.class.equals(clazz);
    }
}
